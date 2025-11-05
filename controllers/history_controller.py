from flask import Blueprint, request, jsonify
from services.history_service import HistoryService
from middleware.auth_middleware import require_auth

history_bp = Blueprint("history", __name__)

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
