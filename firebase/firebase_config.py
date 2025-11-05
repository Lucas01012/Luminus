import firebase_admin
from firebase_admin import credentials, storage, firestore, auth

# Inicializa Firebase Admin SDK com suas credenciais
cred = credentials.Certificate("credentials/firebase-service-account.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'luminus-2d0bd.firebasestorage.app'  # ✅ Seu bucket real
})

# Exporta clientes para uso em outros módulos
db = firestore.client()
bucket = storage.bucket()
auth_client = auth