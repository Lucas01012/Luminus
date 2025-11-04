import os
import google.generativeai as genai

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