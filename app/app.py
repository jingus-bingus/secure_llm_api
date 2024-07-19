from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from transformers import LlamaForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
from flask_cors import CORS
import os
from routes import conversation
from routes.authentication import auth_bp
from config import Config

app = Flask(__name__)
CORS(app)
app.secret_key = Config.SECRET_KEY

# create config for oauth
app.config.from_object(Config)

app.config['UPLOAD_FOLDER'] = './files'
app.config['ALLOWED_EXTENSIONS'] = {'pdf',}

# creates config for quanitization
bits_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)

# load model to app.config with quantization config
app.config['MODEL'] = LlamaForCausalLM.from_pretrained("../../Meta-Llama-3-8B-Instruct", quantization_config=bits_config)
app.config['TOKENIZER'] = AutoTokenizer.from_pretrained("../../Meta-Llama-3-8B-Instruct")

# add blueprint from routes/conversation  and routes/auth_bp
app.register_blueprint(conversation)
app.register_blueprint(auth_bp)

CERT_FILE = "./ssl_context/cert.pem"
KEY_FILE = "./ssl_context/key.pem"

app.config['KEY'] = 'dummy_key'

def start_server():
    context = ("./ssl_context/cert.pem", "./ssl_context/key.pem")
    app.run(debug=True, ssl_context=context, use_reloader=False)

if __name__ == '__main__':
    start_server()