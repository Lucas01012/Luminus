from flask import Blueprint, request, jsonify
from services.image_service import process_image

image_bp = Blueprint("image", __name__)

@image_bp.route("/analisar", methods=["POST"])

def analisar():
    if "imagem" not in request.files:
        return jsonify({"erro":"Nenhuma imagem foi enviada"}), 400
    
    imagem = request.files["imagem"]
    resultado = process_image(imagem)
    return jsonify(resultado)