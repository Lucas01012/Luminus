from firebase.firebase_config import auth_client
from firebase_admin import auth

class AuthService:
    
    @staticmethod
    def verify_token(id_token):
        """
        Verifica se o token JWT do Firebase é válido
        
        Args:
            id_token: Token JWT enviado pelo frontend
            
        Returns:
            dict com sucesso=True e dados do usuário, ou sucesso=False e erro
        """
        try:
            if id_token.startswith('Bearer '):
                id_token = id_token.replace('Bearer ', '')
            
            decoded_token = auth.verify_id_token(id_token)
            
            return {
                "sucesso": True,
                "uid": decoded_token['uid'],
                "email": decoded_token.get('email'),
                "email_verified": decoded_token.get('email_verified', False)
            }
        except auth.InvalidIdTokenError:
            return {
                "sucesso": False,
                "erro": "Token inválido ou expirado"
            }
        except auth.ExpiredIdTokenError:
            return {
                "sucesso": False,
                "erro": "Token expirado"
            }
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro ao verificar token: {str(e)}"
            }