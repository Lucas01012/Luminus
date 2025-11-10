from flask import Blueprint, request, jsonify
from services.image_service import process_image_gemini
from services.history_service import HistoryService
from utils.image_optimizer import ImageOptimizer
from middleware.auth_middleware import optional_auth
import traceback
import time
import io

image_bp = Blueprint("image", __name__)


@image_bp.route("/analisar", methods=["POST"])
@optional_auth
def analisar():
    """
    Analisa imagem com Gemini AI (descrição detalhada para acessibilidade)
    """
    start_time = time.time()
    
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhuma imagem foi enviada"}), 400

    imagem = request.files["imagem"]
    imagem_nome = imagem.filename

    try:
        # Lê a imagem original para salvar no histórico
        imagem_original = io.BytesIO(imagem.read())
        imagem.seek(0)  # Reseta para processar
        
        optimizer_result = ImageOptimizer.optimize_for_ai(imagem, max_size=(512, 512), quality=70)
        
        if optimizer_result["success"]:
            optimized_image = optimizer_result["optimized_image"]
            print(f"Imagem otimizada: {optimizer_result['compression_ratio']}% menor")
        else:
            optimized_image = imagem
            imagem.seek(0)
        
        resultado = process_image_gemini(optimized_image)
        
        processing_time = time.time() - start_time
        resultado[0]["processing_time"] = round(processing_time, 2)
        
        # Salvar no histórico se o usuário estiver autenticado
        if hasattr(request, 'user_id') and request.user_id:
            try:
                HistoryService.save_image_analysis(
                    user_id=request.user_id,
                    image_name=imagem_nome,
                    analysis_result=resultado[0],
                    image_file=imagem_original  # ← Passa a imagem original
                )
                print(f"✅ Histórico salvo para usuário {request.user_id}")
            except Exception as hist_error:
                print(f"⚠️ Erro ao salvar histórico: {hist_error}")
                # Não falha a requisição se o histórico falhar
        
        return jsonify(resultado[0])
        
    except Exception as e:
        print("ERRO AO PROCESSAR IMAGEM:")
        traceback.print_exc()
        return jsonify({"erro": f"Erro no processamento: {str(e)}"}), 500


@image_bp.route("/analisar-rapido", methods=["POST"])
@optional_auth
def analisar_rapido():
    """
    Versão otimizada para máxima velocidade
    """
    start_time = time.time()
    
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhuma imagem foi enviada"}), 400

    imagem = request.files["imagem"]
    imagem_nome = imagem.filename
    
    try:
        # Lê a imagem original para salvar no histórico
        imagem_original = io.BytesIO(imagem.read())
        imagem.seek(0)
        
        quick_image = ImageOptimizer.quick_resize(imagem, target_size=(256, 256))
        if not quick_image:
            quick_image = imagem
            imagem.seek(0)
        
        resultado = process_image_gemini(quick_image)
        
        processing_time = time.time() - start_time
        resultado[0]["processing_time"] = round(processing_time, 2)
        resultado[0]["mode"] = "rapido"
        
        # Salvar no histórico se autenticado
        if hasattr(request, 'user_id') and request.user_id:
            try:
                HistoryService.save_image_analysis(
                    user_id=request.user_id,
                    image_name=imagem_nome,
                    analysis_result=resultado[0],
                    image_file=imagem_original  # ← Passa a imagem original
                )
            except Exception as hist_error:
                print(f"⚠️ Erro ao salvar histórico: {hist_error}")
        
        return jsonify(resultado[0])
        
    except Exception as e:
        return jsonify({"erro": f"Erro no processamento rápido: {str(e)}"}), 500


@image_bp.route("/analisar-ultra", methods=["POST"])
@optional_auth
def analisar_ultra_rapido():
    """Versão ultra-otimizada para máxima velocidade (sub 3 segundos)"""
    start_time = time.time()
    
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhuma imagem foi enviada"}), 400

    imagem = request.files["imagem"]
    imagem_nome = imagem.filename
    
    try:
        # Lê a imagem original para salvar no histórico
        imagem_original = io.BytesIO(imagem.read())
        imagem.seek(0)
        
        compressed_image = ImageOptimizer.compress_for_api(
            imagem, 
            max_size=(256, 256),
            quality=30,
            optimize=True
        )
        
        resultado = process_image_gemini(compressed_image)
        
        processing_time = round(time.time() - start_time, 2)
        
        response_data = {
            "objeto": resultado[0]["objeto"] if resultado else "Não foi possível analisar",
            "tempo_processamento": f"{processing_time}s",
            "modo": "ultra-rapido"
        }
        
        # Salvar no histórico se autenticado
        if hasattr(request, 'user_id') and request.user_id:
            try:
                full_resultado = resultado[0].copy() if resultado else {}
                full_resultado["processing_time"] = processing_time
                HistoryService.save_image_analysis(
                    user_id=request.user_id,
                    image_name=imagem_nome,
                    analysis_result=full_resultado,
                    image_file=imagem_original  # ← Passa a imagem original
                )
            except Exception as hist_error:
                print(f"⚠️ Erro ao salvar histórico: {hist_error}")
        
        response = jsonify(response_data)
        
        response.headers['Cache-Control'] = 'no-cache, no-store'
        response.headers['Connection'] = 'close'
        
        return response
        
    except Exception as e:
        processing_time = round(time.time() - start_time, 2)
        return jsonify({
            "erro": str(e),
            "tempo_processamento": f"{processing_time}s"
        }), 500


