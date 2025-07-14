import base64
from google.cloud import vision
import google.generativeai as genai

# Configure a API key (se ainda não tiver feito isso em outro lugar)
genai.configure(api_key='AIzaSyBAWEIDFjauo5RMdkWH8mKagJDdc1XehT4')

models = genai.list_models()
for model in models:
    print(model.name)

def process_image_vision(image_file):
    client = vision.ImageAnnotatorClient()
    content = image_file.read()
    image = vision.Image(content=content)

    label_response = client.label_detection(image=image)
    labels = label_response.label_annotations

    web_response = client.web_detection(image=image)
    web_entities = web_response.web_detection.web_entities

    result = {
        "labels": [],
        "web_entities": []
    }

    for label in labels[:3]:
        result["labels"].append({
            "objeto": label.description,
            "confianca": round(label.score, 2)
        })

    if web_entities:
        for entity in web_entities[:3]:
            if entity.description:
                result["web_entities"].append({
                    "descricao": entity.description,
                    "score": round(entity.score, 2)
                })

    return result

def process_image_gemini(image_file):
    content = image_file.read()

    model = genai.GenerativeModel(model_name="gemini-2.5-flash")

    response = model.generate_content(
        [
            "Descreva a imagem como se estivesse explicando para uma pessoa cega. Fale de todos os detalhes visuais possíveis, em texto contínuo, sem usar listas ou JSON.",
            {
                "mime_type": "image/jpeg",
                "data": content
            }
        ]
    )

    return [{
        "objeto": response.text.strip(),
        "confianca": None
    }]