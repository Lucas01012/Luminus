from flask import Blueprint, request, jsonify
from services.image_service import process_image_vision, process_image_gemini
from google.cloud import vision  # necessário para o OCR
from utils.image_optimizer import ImageOptimizer
import traceback
import time

image_bp = Blueprint("image", __name__)


@image_bp.route("/analisar", methods=["POST"])
def analisar():
    start_time = time.time()
    
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhuma imagem foi enviada"}), 400

    imagem = request.files["imagem"]
    modo = request.args.get("modo", "gemini")

    try:
        # Otimiza imagem
        if modo == "vision":
            optimizer_result = ImageOptimizer.optimize_for_ai(imagem, max_size=(800, 800), quality=85)
        else:
            optimizer_result = ImageOptimizer.optimize_for_ai(imagem, max_size=(512, 512), quality=70)
        
        if optimizer_result["success"]:
            optimized_image = optimizer_result["optimized_image"]
            print(f"Otimização: {optimizer_result['compression_ratio']}% menor - {optimizer_result['optimized_size']} bytes")
        else:
            optimized_image = imagem
            imagem.seek(0)
        
        # Processa com imagem otimizada
        if modo == "vision":
            resultado = process_image_vision(optimized_image)
        else:
            resultado = process_image_gemini(optimized_image)
        
        processing_time = time.time() - start_time
        # Corrigido: resultado é lista
        resultado[0]["processing_time"] = round(processing_time, 2)
        
        return jsonify(resultado[0])
        
    except Exception as e:
        print("ERRO AO PROCESSAR IMAGEM:")
        traceback.print_exc()
        return jsonify({"erro": f"Erro no processamento: {str(e)}"}), 500


@image_bp.route("/analisar-rapido", methods=["POST"])
def analisar_rapido():
    """
    Versão otimizada para máxima velocidade
    """
    start_time = time.time()
    
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhuma imagem foi enviada"}), 400

    imagem = request.files["imagem"]
    
    try:
        # Redimensionamento ultra-rápido
        quick_image = ImageOptimizer.quick_resize(imagem, target_size=(256, 256))
        if not quick_image:
            quick_image = imagem
            imagem.seek(0)
        
        # Só Gemini (mais rápido que Vision)
        resultado = process_image_gemini(quick_image)
        
        processing_time = time.time() - start_time
        resultado[0]["processing_time"] = round(processing_time, 2)
        resultado[0]["mode"] = "rapido"
        
        return jsonify(resultado[0])
        
    except Exception as e:
        return jsonify({"erro": f"Erro no processamento rápido: {str(e)}"}), 500


@image_bp.route("/analisar-ultra", methods=["POST"])
def analisar_ultra_rapido():
    """Versão ultra-otimizada para máxima velocidade (sub 3 segundos)"""
    start_time = time.time()
    
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhuma imagem foi enviada"}), 400

    imagem = request.files["imagem"]
    
    try:
        # Compressão extrema para velocidade máxima
        compressed_image = ImageOptimizer.compress_for_api(
            imagem, 
            max_size=(256, 256),  # Mínimo possível
            quality=30,           # Qualidade mínima aceitável
            optimize=True
        )
        
        # Apenas Gemini com configuração ultra-rápida
        resultado = process_image_gemini(compressed_image)
        
        processing_time = round(time.time() - start_time, 2)
        
        response_data = {
            "objeto": resultado[0]["objeto"] if resultado else "Não foi possível analisar",
            "tempo_processamento": f"{processing_time}s",
            "modo": "ultra-rapido"
        }
        
        response = jsonify(response_data)
        
        # Headers para performance
        response.headers['Cache-Control'] = 'no-cache, no-store'
        response.headers['Connection'] = 'close'
        
        return response
        
    except Exception as e:
        processing_time = round(time.time() - start_time, 2)
        return jsonify({
            "erro": str(e),
            "tempo_processamento": f"{processing_time}s"
        }), 500


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