from flask import Flask, session
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

# creates config for quanitization
bits_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)

# load model to app.config with quantization config
app.config['MODEL'] = LlamaForCausalLM.from_pretrained("../../Meta-Llama-3-8B-Instruct", quantization_config=bits_config)
app.config['TOKENIZER'] = AutoTokenizer.from_pretrained("../../Meta-Llama-3-8B-Instruct")

# add blueprint from routes/conversation  and routes/auth_bp
app.register_blueprint(conversation)
app.register_blueprint(auth_bp)

def start_server():
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    start_server()