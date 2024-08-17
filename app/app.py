from flask import Flask
from transformers import LlamaForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
from flask_cors import CORS
from routes import conversation, upload
from routes.authentication import auth_bp
from config import Config

import logging
logging.basicConfig(filename='record.log', level=logging.DEBUG, 
                    format= '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

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
app.register_blueprint(upload)

CERT_FILE = "./ssl_context/cert.pem"
KEY_FILE = "./ssl_context/key.pem"

# dummy key for development
app.config['KEY'] = 'CvrjvqJVYHKbhA3rO7JoJoDJoJxiv1ssSxsVlx-DRfE='

def start_server():
    context = ("./ssl_context/cert.pem", "./ssl_context/key.pem")
    app.run(debug=True, ssl_context=context, use_reloader=False)

if __name__ == '__main__':
    start_server()


# Unseal Key 1: da2hPvFkZmzEavbX6W+/sYdYVqtxRtuBu01McJPAchNx
# Unseal Key 2: hpbew43L9FQoNRMyWqfZOIKPndhxxKynnk6ZEA/00noq
# Unseal Key 3: DTcOCY7StKFAAE53zdDNOmTgB3PUKZdlb8HuhJgvEikL
# Unseal Key 4: nCCwn3fEbcCEHCrsJ/+uL98iput0SxxP9ECcEbKUcZ6E
# Unseal Key 5: /Iw3DuVD2sSiB57zgS4JxLNx07ebQQW1Qlq3G2DGi0BR

# Initial Root Token: hvs.Qx0jI7p96jjCVW9LS9TkTdSw

# Key                  Value
# ---                  -----
# token                hvs.Qx0jI7p96jjCVW9LS9TkTdSw
# token_accessor       n4kXO1JPtba8W6UipDbsRB88
# token_duration       ∞
# token_renewable      false
# token_policies       ["root"]
# identity_policies    []
# policies             ["root"]

