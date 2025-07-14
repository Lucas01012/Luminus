from flask import Blueprint, request, jsonify
from services.image_service import process_image_vision, process_image_gemini
from google.cloud import vision  # necessário para o OCR

image_bp = Blueprint("image", __name__)


@image_bp.route("/analisar", methods=["POST"])
def analisar():
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhuma imagem foi enviada"}), 400

    imagem = request.files["imagem"]
    modo = request.args.get("modo", "gemini")  # ?modo=vision ou ?modo=gemini

    if modo == "vision":
        resultado = process_image_vision(imagem)
    else:
        resultado = process_image_gemini(imagem)

    return jsonify(resultado)


@image_bp.route("/ler-texto", methods=["POST"])
def analisar_texto_imagem():
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhuma imagem foi enviada"}), 400

    imagem = request.files["imagem"]
    
    client = vision.ImageAnnotatorClient()
    content = imagem.read()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    texto_detectado = texts[0].description if texts else "Nenhum texto detectado"

    return jsonify({"texto": texto_detectado})