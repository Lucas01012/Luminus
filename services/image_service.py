import os
import io
import google.generativeai as genai

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
            "max_output_tokens": 150,
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
                'HARASSMENT': 'block_none',
                'HATE_SPEECH': 'block_none',
                'SEXUALLY_EXPLICIT': 'block_none',
                'DANGEROUS_CONTENT': 'block_none'
            }
        )

        if not response.parts:
            finish_reason = getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None
            
            if finish_reason == 2:
                return [{
                    "objeto": "Não foi possível analisar esta imagem devido a restrições de segurança. Tente outra imagem.",
                    "confianca": None
                }]
            elif finish_reason == 3:
                return [{
                    "objeto": "Imagem bloqueada por conter conteúdo protegido por direitos autorais.",
                    "confianca": None
                }]
            else:
                print(f"Gemini retornou resposta vazia. finish_reason={finish_reason}")
                return [{
                    "objeto": "Não foi possível processar esta imagem. Verifique o formato e tente novamente.",
                    "confianca": None
                }]

        return [{
            "objeto": response.text.strip(),
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