from google.cloud import vision
from google.cloud.vision_v1 import types

def process_image(image_file):
    client = vision.ImageAnnotatorClient()

    content = image_file.read()

    image = vision.Image(content = content)

    response = client.label_detection(image = image)
    labels = response.label_annotations

    web_response = client.web_detection(image=image)
    web_entities = web_response.web_detection.web_entities

    result = {
        "labels":[],
        "web_entities":[]
    }

    for label in labels[:3]:
        result["labels"].append({
            "objeto": label.description,
            "confianca": round(label.score, 2)
        })

    if web_entities:
        for entity in web_entities[:3]:
            result["web_entities"].append({
                "descricao": entity.description,
                "score": round(entity.score, 2)
            })

    return result