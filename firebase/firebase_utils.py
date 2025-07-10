from firebase.firebase_config import bucket, db
import datetime

def upload_image_storage(image, archive_name):
    blob = bucket.blob(f"uploads/{"archive_name"}")
    blob.upload_from_file(image)
    blob.make_public()
    return blob.public_url

def save_image_firestore(user_id, result):
    doc_ref = db.collection("analises").document()
    doc_ref.set({
        "usuario": user_id,
        "resultado": result,
        "data":datetime.datetime.now()

    })
