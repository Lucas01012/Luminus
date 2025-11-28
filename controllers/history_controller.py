from flask import Blueprint, request, jsonify
from services.history_service import HistoryService
from middleware.auth_middleware import require_auth
import base64
import io

history_bp = Blueprint("history", __name__)


@history_bp.route("/salvar-imagem", methods=["POST"])
@require_auth
def salvar_imagem_manual():
    """
    Endpoint para o frontend salvar análise de imagem manualmente
    
    Headers:
    - Authorization: Bearer <token>
    
    Body (JSON):
    {
      "image_name": "foto.jpg",
      "image_base64": "data:image/jpeg;base64,/9j/4AAQ..." (opcional),
      "analysis_result": {
        "objeto_detectado": "Um cachorro...",
        "confianca": 0.95,
        "processing_time": 2.34,
        "descricao": "Descrição..."
      }
    }
    
    Retorna:
    - doc_id: ID do documento criado no Firestore
    - imagem_url: URL da imagem no Firebase Storage (se image_base64 fornecido)
    """
    user_id = request.user_id
    data = request.get_json()
    
    if not data:
        return jsonify({"sucesso": False, "erro": "Dados não fornecidos"}), 400
    
    image_name = data.get('image_name')
    analysis_result = data.get('analysis_result', {})
    image_base64 = data.get('image_base64')
    
    if not image_name:
        return jsonify({"sucesso": False, "erro": "image_name é obrigatório"}), 400
    
    try:
        image_file = None
        if image_base64:
            try:
                if ',' in image_base64:
                    image_base64 = image_base64.split(',', 1)[1]
                
                image_bytes = base64.b64decode(image_base64)
                image_file = io.BytesIO(image_bytes)
                print(f"Imagem base64 decodificada: {len(image_bytes)} bytes")
            except Exception as b64_error:
                print(f"Erro ao decodificar base64: {b64_error}")
        
        resultado = HistoryService.save_image_analysis(
            user_id=user_id,
            image_name=image_name,
            analysis_result=analysis_result,
            image_file=image_file
        )
        
        if not resultado['sucesso']:
            return jsonify(resultado), 500
        
        return jsonify(resultado), 200
        
    except Exception as e:
        print(f"Erro em salvar_imagem_manual: {str(e)}")
        return jsonify({"sucesso": False, "erro": f"Erro ao salvar: {str(e)}"}), 500


@history_bp.route("/salvar-documento", methods=["POST"])
@require_auth
def salvar_documento_manual():
    """
    Endpoint para o frontend salvar processamento de documento manualmente
    
    Headers:
    - Authorization: Bearer <token>
    
    Body (JSON):
    {
      "file_name": "documento.pdf",
      "document_result": {
        "text_content": "Conteúdo do documento...",
        "resumo": "Resumo do documento",
        "palavras_chave": ["palavra1", "palavra2"],
        "metadata": {
          "total_pages": 5
        },
        "arquivo_info": {
          "formato": "pdf",
          "tamanho_bytes": 54321
        }
      }
    }
    
    Retorna:
    - doc_id: ID do documento criado no Firestore
    """
    user_id = request.user_id
    data = request.get_json()
    
    if not data:
        return jsonify({"sucesso": False, "erro": "Dados não fornecidos"}), 400
    
    file_name = data.get('file_name')
    document_result = data.get('document_result', {})
    
    if not file_name:
        return jsonify({"sucesso": False, "erro": "file_name é obrigatório"}), 400
    
    try:
        resultado = HistoryService.save_document_analysis(
            user_id=user_id,
            file_name=file_name,
            document_result=document_result
        )
        
        if not resultado['sucesso']:
            return jsonify(resultado), 500
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({"sucesso": False, "erro": f"Erro ao salvar: {str(e)}"}), 500


@history_bp.route("/imagens", methods=["GET"])
@require_auth
def listar_historico_imagens():
    """
    Lista histórico de análises de imagens do usuário autenticado
    
    Headers:
    - Authorization: Bearer <token>
    
    Query params:
    - limit: Número máximo de resultados (opcional, padrão: 20)
    
    Retorna:
    - Lista de análises de imagens
    """
    user_id = request.user_id
    limit = request.args.get("limit", 20, type=int)
    
    try:
        resultado = HistoryService.get_user_image_history(user_id, limit)
        
        if not resultado['sucesso']:
            return jsonify(resultado), 500
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar histórico: {str(e)}"}), 500


@history_bp.route("/documentos", methods=["GET"])
@require_auth
def listar_historico_documentos():
    """
    Lista histórico de documentos processados do usuário autenticado
    
    Headers:
    - Authorization: Bearer <token>
    
    Query params:
    - limit: Número máximo de resultados (opcional, padrão: 20)
    
    Retorna:
    - Lista de documentos processados
    """
    user_id = request.user_id
    limit = request.args.get("limit", 20, type=int)
    
    try:
        resultado = HistoryService.get_user_document_history(user_id, limit)
        
        if not resultado['sucesso']:
            return jsonify(resultado), 500
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar histórico: {str(e)}"}), 500


@history_bp.route("/completo", methods=["GET"])
@require_auth
def listar_historico_completo():
    """
    Lista histórico completo (imagens + documentos) do usuário
    
    Headers:
    - Authorization: Bearer <token>
    
    Query params:
    - limit: Número máximo de resultados (opcional, padrão: 30)
    
    Retorna:
    - Lista combinada de imagens e documentos, ordenada por data
    """
    user_id = request.user_id
    limit = request.args.get("limit", 30, type=int)
    
    try:
        resultado = HistoryService.get_user_full_history(user_id, limit)
        
        if not resultado['sucesso']:
            return jsonify(resultado), 500
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar histórico: {str(e)}"}), 500


@history_bp.route("/deletar/<tipo>/<doc_id>", methods=["DELETE"])
@require_auth
def deletar_item_historico(tipo, doc_id):
    """
    Deleta um item do histórico
    
    Headers:
    - Authorization: Bearer <token>
    
    Path params:
    - tipo: 'imagem' ou 'documento'
    - doc_id: ID do documento no Firestore
    
    Retorna:
    - Confirmação de deleção ou erro
    """
    user_id = request.user_id
    
    if tipo not in ['imagem', 'documento']:
        return jsonify({"erro": "Tipo inválido. Use 'imagem' ou 'documento'"}), 400
    
    try:
        resultado = HistoryService.delete_history_item(user_id, doc_id, tipo)
        
        if not resultado['sucesso']:
            return jsonify(resultado), 403 if 'autorizado' in resultado.get('erro', '') else 404
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao deletar: {str(e)}"}), 500
