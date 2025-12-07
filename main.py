import os
from flask import Flask
from flask_cors import CORS
from controllers.image_controller import image_bp
from controllers.document_controller import document_bp
from controllers.auth_controller import auth_bp
from dotenv import load_dotenv

load_dotenv()
google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_creds:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_creds

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(image_bp)
app.register_blueprint(document_bp, url_prefix="/documento")

@app.route("/")
def home():
    return "Está rodando cidadão"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
