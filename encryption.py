import rsa
import base64
import os
from dotenv import load_dotenv


load_dotenv()

PUBLIC_KEY = os.getenv('PUBLIC_KEY')
PASSWORD = os.getenv('PASSWORD')


def encrypt_rsa(message=PASSWORD, public_key_string=PUBLIC_KEY):
    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key_string.encode('utf-8'))
    encrypted_message = rsa.encrypt(message.encode('utf-8'), public_key)
    return base64.b64encode(encrypted_message).decode('utf-8')


if __name__ == '__main__':
    encrypted_password = encrypt_rsa(PASSWORD, PUBLIC_KEY)
    print(encrypted_password)
