import os
import io
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

genai_api_key = os.getenv("GOOGLE_API_KEY")
if genai_api_key:
    try:
        genai.configure(api_key=genai_api_key)
    except Exception as _:
        pass


def _detect_mime_type_from_filename(filename: str) -> str:
    if not filename:
        return "image/jpeg"
    ext = filename.split('.')[-1].lower()
    return {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'webp': 'image/webp',
        'gif': 'image/gif'
    }.get(ext, 'image/jpeg')


def process_image_gemini(image_file):
    """Processa uma imagem usando o Gemini (flash) e retorna um dict simples.

    image_file pode ser um FileStorage (Flask), BytesIO ou bytes.
    """
    try:
        if not getattr(genai, '_api_key', None):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        if hasattr(image_file, 'seek'):
            try:
                image_file.seek(0)
            except Exception:
                pass

        if hasattr(image_file, 'getvalue'):
            content = image_file.getvalue()
        elif hasattr(image_file, 'read'):
            content = image_file.read()
        elif isinstance(image_file, (bytes, bytearray)):
            content = bytes(image_file)
        else:
            content = b''

        filename = getattr(image_file, 'filename', None)
        mime_type = _detect_mime_type_from_filename(filename)

        generation_config = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 20,
            "max_output_tokens": 1024,
            "candidate_count": 1,
        }

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=generation_config
        )

        prompt = "Em 2 frases: o que você vê nesta imagem? Seja direto e claro."
        response = model.generate_content(
            [
                prompt,
                {
                    "mime_type": mime_type,
                    "data": content
                }
            ],
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        print(f"[DEBUG] Response candidates: {len(response.candidates) if response.candidates else 0}")
        if response.candidates:
            candidate = response.candidates[0]
            print(f"[DEBUG] Finish reason: {candidate.finish_reason}")
            print(f"[DEBUG] Safety ratings: {candidate.safety_ratings}")
            print(f"[DEBUG] Has parts: {bool(response.parts)}")
        
        try:
            text_result = response.text.strip()
            if text_result:
                return [{
                    "objeto": text_result,
                    "confianca": None
                }]
        except ValueError as ve:
            print(f"[DEBUG] Erro ao acessar response.text: {ve}")
        
        if response.candidates:
            finish_reason = response.candidates[0].finish_reason
            safety_ratings = response.candidates[0].safety_ratings
            
            print(f"[DEBUG] Imagem bloqueada. Finish reason: {finish_reason}, Safety: {safety_ratings}")
            
            if finish_reason == 3:
                return [{
                    "objeto": f"A API bloqueou esta imagem por segurança mesmo com filtros desabilitados. Ratings: {safety_ratings}",
                    "confianca": None
                }]
            elif finish_reason == 4:
                return [{
                    "objeto": "Imagem bloqueada por conter conteúdo protegido por direitos autorais.",
                    "confianca": None
                }]
            else:
                return [{
                    "objeto": f"Resposta vazia da API. Finish reason: {finish_reason}. Tente outra imagem.",
                    "confianca": None
                }]
        
        return [{
            "objeto": "Não foi possível processar esta imagem. Verifique o formato e tente novamente.",
            "confianca": None
        }]

    except Exception as e:
        error_msg = str(e)
        print(f"Erro no Gemini: {error_msg}")
        
        if "finish_reason" in error_msg and "2" in error_msg:
            return [{
                "objeto": "Não foi possível analisar esta imagem devido a restrições de segurança. Tente outra imagem.",
                "confianca": None
            }]
        elif "Invalid image" in error_msg or "invalid" in error_msg.lower():
            return [{
                "objeto": "Formato de imagem inválido. Use JPG, PNG ou WebP.",
                "confianca": None
            }]
        else:
            return [{
                "objeto": f"Erro ao processar imagem: {error_msg}",
                "confianca": None
            }]