import firebase
from firebase import credentials, storage, firestore

cred = credentials.Certificate("firebase-creds.json")
firebase.initialize_app(cred, {
    'storageBucket':'meu.projeto.appspot.com'
})

db = firebase.client()
bucket = storage.bucket()