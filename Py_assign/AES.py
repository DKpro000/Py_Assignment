import hashlib
import base64
import random

# 简单 Diffie-Hellman 密钥交换
class KeyExchange:
    def __init__(self, g=5, p=97):
        self.g = g
        self.p = p
        self.private = random.randint(1, 50)
        self.public = pow(g, self.private, p)

    def generate_shared_key(self, other_public):
        shared_secret = pow(other_public, self.private, self.p)
        return hashlib.sha256(str(shared_secret).encode()).digest()  # 32字节密钥

# 手写对称加密（类 AES 概念，3轮简单轮换+替换）
def pseudo_encrypt(data: str, key: bytes, rounds: int = 3) -> str:
    data_bytes = data.encode()
    for r in range(rounds):
        data_bytes = bytes([(b ^ key[(i + r) % len(key)]) ^ ((i + r) * 13 % 256) for i, b in enumerate(data_bytes)])
    return base64.b64encode(data_bytes).decode()

def pseudo_decrypt(enc_data: str, key: bytes, rounds: int = 3) -> str:
    data_bytes = base64.b64decode(enc_data)
    for r in reversed(range(rounds)):
        data_bytes = bytes([(b ^ ((i + r) * 13 % 256)) ^ key[(i + r) % len(key)] for i, b in enumerate(data_bytes)])
    return data_bytes.decode()