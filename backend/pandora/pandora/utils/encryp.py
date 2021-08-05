import os
from hashlib import sha256
from hmac import HMAC
import base64
from jwkest.jwk import SYMKey
from jwkest.jws import JWS
import sys
# from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

salt_len = 8


def simple_encrypt(data):
    return base64.b64encode(data.encode()).decode()


def simple_decrypt(data):
    return base64.b64decode(data.encode()).decode()


def asymmetric_encrypt(data, salt=None):
    if not salt:
        salt = os.urandom(salt_len)
    result = data

    assert salt_len == len(salt)
    assert isinstance(salt, str)

    for i in range(10):
        result = HMAC(result, salt, sha256).digest()

    return salt + result


def encode_json_to_token(payload, salt="idaas_login", jwt_alg="HS256"):
    keys = [SYMKey(key=salt, alg=jwt_alg)]
    _jws = JWS(payload, alg=jwt_alg)
    return _jws.sign_compact(keys)


def decode_json_from_token(token, salt="idaas_login", jwt_alg="HS256"):
    keys = [SYMKey(key=salt, alg=jwt_alg)]
    return JWS().verify_compact(token, keys=keys)


def authenticate_data(ciphertext, plaintext):
    return ciphertext == asymmetric_encrypt(plaintext, ciphertext[:8])

# session_len = 16
#
#
# class Symmetric(object):
#     def __init__(self, key):
#         assert len(key) == session_len
#         self.key = key
#         self.mode = AES.MODE_CBC
#
#     # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
#     def encrypt(self, text):
#         cryptor = AES.new(self.key, self.mode, self.key[::-1])
#         # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
#         length = session_len
#         count = len(text)
#         add = length - (count % length)
#         text = text + ("\0" * add)
#         self.ciphertext = cryptor.encrypt(text)
#         # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
#         # 所以这里统一把加密后的字符串转化为16进制字符串
#         return b2a_hex(self.ciphertext)
#
#     # 解密后，去掉补足的空格用strip() 去掉
#     def decrypt(self, text):
#         cryptor = AES.new(self.key, self.mode, self.key[::-1])
#         plain_text = cryptor.decrypt(a2b_hex(text))
#         plain_text = plain_text.decode() if isinstance(plain_text, bytes) else plain_text
#         return plain_text.rstrip("\0")
