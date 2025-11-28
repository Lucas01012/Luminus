import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("credentials/firebase-service-account.json")
firebase_admin.initialize_app(cred)

auth_client = auth