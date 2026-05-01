import os

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_aes_key():
    """
    สร้าง AES key ขนาด 256-bit
    """
    return AESGCM.generate_key(bit_length=256)


def generate_rsa_keys():
    """
    สร้าง RSA private/public key
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    return private_key, public_key


def encrypt_data_with_aes(data_bytes, aes_key):
    """
    ใช้ AES-GCM เข้ารหัส bytes ของไฟล์โมเดลทั้งชุด
    """
    aesgcm = AESGCM(aes_key)

    nonce = os.urandom(12)
    encrypted_data = aesgcm.encrypt(nonce, data_bytes, None)

    return nonce, encrypted_data


def decrypt_data_with_aes(nonce, encrypted_data, aes_key):
    """
    ใช้ AES-GCM ถอดรหัส bytes ของไฟล์โมเดลทั้งชุด
    """
    aesgcm = AESGCM(aes_key)

    decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)

    return decrypted_data


def encrypt_aes_key_with_rsa(aes_key, rsa_public_key):
    """
    ใช้ RSA Public Key เข้ารหัส AES Key
    """
    encrypted_aes_key = rsa_public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_aes_key


def decrypt_aes_key_with_rsa(encrypted_aes_key, rsa_private_key):
    """
    ใช้ RSA Private Key ถอดรหัส AES Key
    """
    aes_key = rsa_private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return aes_key