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
            optimized_image = image_file
            image_file.seek(0)
        
        client = vision.ImageAnnotatorClient()
        content = optimized_image.read()
        image = vision.Image(content=content)

        label_response = client.label_detection(image=image)
        labels = label_response.label_annotations

        # web_response = client.web_detection(image=image)
        # web_entities = web_response.web_detection.web_entities

        result = {
            "labels": [],
        }

        for label in labels[:3]:
            if label.score > 0.7:
                result["labels"].append({
                    "objeto": label.description,
                    "confianca": round(label.score, 2)
                })

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
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        if hasattr(image_file, 'getvalue'):
            content = image_file.getvalue()
        else:
            content = image_file.read()

        generation_config = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 20,
            "max_output_tokens": 150,
        }

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config
        )

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