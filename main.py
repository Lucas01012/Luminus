import os
from flask import Flask
from flask_cors import CORS
from controllers.image_controller import image_bp
from controllers.document_controller import document_bp
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

app = Flask(__name__)
CORS(app)
app.register_blueprint(image_bp)
app.register_blueprint(document_bp, url_prefix="/documento")

@app.route("/")
def home():
    return "Está rodando cidadão"

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
