from firebase.firebase_config import auth_client, db
from firebase_admin import auth, firestore

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
    
    @staticmethod
    def get_user_info(uid):
        """
        Busca informações do usuário no Firestore
        
        Args:
            uid: ID único do usuário no Firebase
            
        Returns:
            dict com dados do usuário ou None
        """
        try:
            user_ref = db.collection('usuarios').document(uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            print(f"Erro ao buscar usuário: {str(e)}")
            return None
    
    @staticmethod
    def create_or_update_user(uid, email, data=None):
        """
        Cria ou atualiza perfil do usuário no Firestore
        
        Args:
            uid: ID único do usuário
            email: Email do usuário
            data: Dados adicionais do perfil (opcional)
            
        Returns:
            bool indicando sucesso
        """
        try:
            user_ref = db.collection('usuarios').document(uid)
            
            user_data = {
                'email': email,
                'ultimo_acesso': firestore.SERVER_TIMESTAMP
            }
            
            if data:
                user_data.update(data)
            
            user_ref.set(user_data, merge=True)
            return True
        except Exception as e:
            print(f"Erro ao criar/atualizar usuário: {str(e)}")
            return False