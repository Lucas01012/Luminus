from services.auth_service import AuthService
from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/verificar-token", methods=["POST"])
def verificar_token():
    """
    Verifica se um token Firebase JWT é válido
    
    Headers:
    - Authorization: Bearer <token>
    
    OU Body JSON:
    - token: <token>
    
    Retorna:
    - sucesso: True/False
    - uid: ID do usuário (se válido)
    - email: Email do usuário
    """
    # Tenta pegar token do header
    token = request.headers.get('Authorization')
    
    # Se não tiver no header, tenta no body
    if not token:
        data = request.get_json()
        if data and 'token' in data:
            token = data['token']
    
    if not token:
        return jsonify({"erro": "Token não fornecido"}), 401
    
    try:
        resultado = AuthService.verify_token(token)
        
        if not resultado['sucesso']:
            return jsonify(resultado), 401
        
        # Atualiza/cria perfil do usuário
        AuthService.create_or_update_user(
            resultado['uid'], 
            resultado.get('email')
        )
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao verificar token: {str(e)}"}), 500


@auth_bp.route("/perfil", methods=["GET"])
def obter_perfil():
    """
    Retorna informações do perfil do usuário autenticado
    
    Headers:
    - Authorization: Bearer <token>
    
    Retorna:
    - Dados do perfil do usuário
    """
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({"erro": "Token não fornecido"}), 401
    
    try:
        # Verifica token
        resultado = AuthService.verify_token(token)
        
        if not resultado['sucesso']:
            return jsonify(resultado), 401
        
        # Busca dados do usuário
        user_info = AuthService.get_user_info(resultado['uid'])
        
        if not user_info:
            return jsonify({
                "uid": resultado['uid'],
                "email": resultado.get('email'),
                "mensagem": "Perfil não encontrado no Firestore"
            }), 200
        
        return jsonify({
            "uid": resultado['uid'],
            "email": resultado.get('email'),
            "perfil": user_info
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar perfil: {str(e)}"}), 500


@auth_bp.route("/atualizar-perfil", methods=["PUT"])
def atualizar_perfil():
    """
    Atualiza informações do perfil do usuário
    
    Headers:
    - Authorization: Bearer <token>
    
    Body JSON:
    - nome: Nome do usuário (opcional)
    - telefone: Telefone (opcional)
    - preferencias: Objeto com preferências (opcional)
    
    Retorna:
    - sucesso: True/False
    """
    token = request.headers.get('Authorization')
    data = request.get_json()
    
    if not token:
        return jsonify({"erro": "Token não fornecido"}), 401
    
    if not data:
        return jsonify({"erro": "Nenhum dado fornecido"}), 400
    
    try:
        # Verifica token
        resultado = AuthService.verify_token(token)
        
        if not resultado['sucesso']:
            return jsonify(resultado), 401
        
        # Atualiza perfil
        sucesso = AuthService.create_or_update_user(
            resultado['uid'],
            resultado.get('email'),
            data
        )
        
        if sucesso:
            return jsonify({"sucesso": True, "mensagem": "Perfil atualizado"}), 200
        else:
            return jsonify({"sucesso": False, "erro": "Falha ao atualizar perfil"}), 500
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao atualizar perfil: {str(e)}"}), 500