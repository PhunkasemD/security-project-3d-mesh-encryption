import os
import pickle
import hashlib


def read_file_as_bytes(file_path):
    """
    อ่านไฟล์เป็น bytes
    """
    with open(file_path, "rb") as file:
        return file.read()


def write_bytes_to_file(file_path, data_bytes):
    """
    เขียน bytes กลับเป็นไฟล์
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as file:
        file.write(data_bytes)


def create_model_package(model_files):
    """
    รวมไฟล์โมเดลทั้งชุดเป็น package เดียว
    """
    package = {}

    for file_name, file_path in model_files.items():
        package[file_name] = read_file_as_bytes(file_path)

    return package


def serialize_package(package):
    """
    แปลง package เป็น bytes เพื่อให้ AES เข้ารหัสได้
    """
    return pickle.dumps(package)


def deserialize_package(package_bytes):
    """
    แปลง bytes กลับเป็น package
    """
    return pickle.loads(package_bytes)


def restore_model_package(package, output_mapping):
    """
    แตก package กลับเป็นไฟล์จริงใน output/
    """
    for file_name, output_path in output_mapping.items():
        if file_name not in package:
            raise FileNotFoundError(f"Missing file in decrypted package: {file_name}")

        write_bytes_to_file(output_path, package[file_name])


def calculate_sha256(file_path):
    """
    คำนวณ SHA-256 hash ของไฟล์
    ใช้ตรวจว่าไฟล์ต้นฉบับกับไฟล์หลังถอดรหัสเหมือนกันระดับ byte หรือไม่
    """
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()