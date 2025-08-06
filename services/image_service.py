import base64
from google.cloud import vision
import google.generativeai as genai
import os
from utils.image_optimizer import ImageOptimizer

def process_image_vision(image_file):
    try:
        # Otimiza imagem primeiro
        optimizer_result = ImageOptimizer.optimize_for_ai(image_file, max_size=(800, 800), quality=80)
        
        if optimizer_result["success"]:
            optimized_image = optimizer_result["optimized_image"]
            print(f"Imagem otimizada: {optimizer_result['compression_ratio']}% menor")
        else:
            # Fallback para imagem original
            optimized_image = image_file
            image_file.seek(0)
        
        client = vision.ImageAnnotatorClient()
        content = optimized_image.read()
        image = vision.Image(content=content)

        # Faz requisições em paralelo quando possível
        label_response = client.label_detection(image=image)
        labels = label_response.label_annotations

        # Só faz web detection se necessário (consome mais tempo)
        # web_response = client.web_detection(image=image)
        # web_entities = web_response.web_detection.web_entities

        result = {
            "labels": [],
            # "web_entities": []
        }

        # Limita a 3 labels mais confiáveis
        for label in labels[:3]:
            if label.score > 0.7:  # Só inclui com alta confiança
                result["labels"].append({
                    "objeto": label.description,
                    "confianca": round(label.score, 2)
                })

        # Comentado para melhorar performance
        # if web_entities:
        #     for entity in web_entities[:3]:
        #         if entity.description:
        #             result["web_entities"].append({
        #                 "descricao": entity.description,
        #                 "score": round(entity.score, 2)
        #             })

        return result
        
    except Exception as e:
        return {"erro": f"Erro no Vision: {str(e)}"}


def process_image_gemini(image_file):
    try:
        # Configura o Gemini com timeout
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Lê conteúdo otimizado
        if hasattr(image_file, 'getvalue'):
            content = image_file.getvalue()
        else:
            content = image_file.read()

        # Configuração otimizada para velocidade
        generation_config = {
            "temperature": 0.1,  # Menos criativo = mais rápido
            "top_p": 0.8,
            "top_k": 20,
            "max_output_tokens": 150,  # Limita resposta = mais rápido
        }

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",  # Modelo mais rápido
            generation_config=generation_config
        )

        # Prompt ultra-otimizado para velocidade
        prompt = "Em 2 frases: o que você vê nesta imagem? Seja direto e claro."

        response = model.generate_content([
            prompt,
            {
                "mime_type": "image/jpeg", 
                "data": content
            }
        ])

        return [{
            "objeto": response.text.strip(),
            "confianca": None
        }]
        
    except Exception as e:
        return [{"objeto": f"Erro no Gemini: {str(e)}", "confianca": None}]