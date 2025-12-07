import firebase_admin
from firebase_admin import credentials, auth
import os

credential_file = os.getenv("FIREBASE_CREDENTIALS", "credentials/firebase-service-account.json")
cred = credentials.Certificate(credential_file)
firebase_admin.initialize_app(cred)

auth_client = auth