import os
import secrets

class Config:
    AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID', 'Vb3DSpfl31iOcVMKMUxYEYSr7JTwRZ92')
    AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET', 'Xe-m70_soPHjIrIjVeIuUQrrSYkC0PVG8HUr6ybjzJ3Kc_0qRtReqbGVg0KAxX9z')
    AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'https://nepsi.auth0.com')
    AUTH0_ACCESS_TOKEN = os.getenv('AUTH0_ACCESS_TOKEN', 'https://nepsi.auth0.com/oauth/token')
    AUTH0_AUTH = os.getenv('AUTH0_AUTH', 'https://nepsi.auth0.com/authorize')
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))