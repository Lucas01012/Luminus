import os
from flask import Flask
from flask_cors import CORS
from controllers.image_controller import image_bp

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_vision_key.json"

app = Flask(__name__)
CORS(app)
app.register_blueprint(image_bp)

@app.route("/")
def home():
        return "Está rodando cidadão"

@app.route("/teste2")
def teste2():
      return "Testando"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
      