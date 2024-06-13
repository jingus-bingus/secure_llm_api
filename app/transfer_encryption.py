from cryptography.hazmat.backends import default_backend
import os

backend = default_backend()
key = os.urandom(32)  # 256-bit key for AES

print(key)
