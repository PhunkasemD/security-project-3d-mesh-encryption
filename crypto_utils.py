import os
import pickle

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# AES = เข้ารหัสข้อมูล vertices/faces จริง
# RSA = เข้ารหัส AES key

def generate_aes_key():
    """
    สร้าง AES key ขนาด 256-bit
    32 bytes = 256 bits
    """
    return AESGCM.generate_key(bit_length=256)


def generate_rsa_keys():
    """
    สร้าง RSA public/private key

    private_key = ใช้ถอดรหัส AES key
    public_key = ใช้เข้ารหัส AES key
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    return private_key, public_key


def serialize_mesh(vertices, faces):
    """
    แปลง vertices และ faces เป็น bytes
    เพื่อให้ AES สามารถนำไปเข้ารหัสได้
    """
    data = {
        "vertices": vertices,
        "faces": faces
    }

    return pickle.dumps(data)


def deserialize_mesh(data_bytes):
    """
    แปลง bytes กลับมาเป็น vertices และ faces
    """
    data = pickle.loads(data_bytes)

    return data["vertices"], data["faces"]


def encrypt_mesh_data(mesh_bytes, aes_key):
    """
    เข้ารหัสข้อมูล mesh ด้วย AES-GCM

    nonce = ค่าสุ่มที่ใช้ร่วมกับ AES-GCM
    encrypted_data = ข้อมูล mesh ที่ถูกเข้ารหัสแล้ว
    """
    aesgcm = AESGCM(aes_key)

    nonce = os.urandom(12)
    encrypted_data = aesgcm.encrypt(nonce, mesh_bytes, None)

    return nonce, encrypted_data


def decrypt_mesh_data(nonce, encrypted_data, aes_key):
    """
    ถอดรหัสข้อมูล mesh ด้วย AES-GCM
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
    ใช้ RSA Private Key ถอดรหัส AES Key กลับมา
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