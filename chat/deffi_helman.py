from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib
import base64


def aes_encrypt(msg, key):
    key = str(key).encode()
    key = hashlib.sha256(key).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    msg = msg + ' ' * (16 - len(msg) % 16)
    return base64.b64encode(cipher.encrypt(msg.encode())).decode()


def aes_decrypt(enc_msg, key):
    key = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    decode = base64.b64decode(enc_msg.encode())
    return cipher.decrypt(decode).decode().strip()


def generate_keys(g, p):
    private_key = int.from_bytes(get_random_bytes(16),'big')
    public_key = pow(g, private_key, p)
    return private_key, public_key


def compute_shared_secret(public_other, private_self, p):
    return str(pow(public_other,private_self, p))
