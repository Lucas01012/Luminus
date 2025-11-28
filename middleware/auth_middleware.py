from flask import request, jsonify
from functools import wraps
from services.auth_service import AuthService

def require_auth(f):
    """
    Decorator para proteger rotas que requerem autenticação
    
    Uso:
        @app.route("/rota-protegida")
        @require_auth
        def minha_rota():
            user_id = request.user_id  # ID do usuário autenticado
            email = request.user_email
            # ... resto do código
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"erro": "Token de autenticação não fornecido"}), 401
        
        resultado = AuthService.verify_token(token)
        
        if not resultado['sucesso']:
            return jsonify({
                "erro": "Token inválido ou expirado",
                "detalhes": resultado.get('erro')
            }), 401
        
        request.user_id = resultado['uid']
        request.user_email = resultado.get('email')
        request.user_verified = resultado.get('email_verified', False)
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    """
    Decorator para rotas que funcionam com ou sem autenticação
    
    Se houver token válido, adiciona user_id ao request
    Se não houver ou for inválido, continua normalmente mas request.user_id será None
    
    Uso:
        @app.route("/rota-opcional")
        @optional_auth
        def minha_rota():
            if request.user_id:
                # Usuário autenticado
                pass
            else:
                # Usuário anônimo
                pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        request.user_id = None
        request.user_email = None
        request.user_verified = False
        
        if token:
            resultado = AuthService.verify_token(token)
            
            if resultado['sucesso']:
                request.user_id = resultado['uid']
                request.user_email = resultado.get('email')
                request.user_verified = resultado.get('email_verified', False)
        
        return f(*args, **kwargs)
    
    return decorated_function
