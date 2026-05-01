import os
import time
import pickle
import statistics

from crypto_utils import (
    generate_aes_key,
    generate_rsa_keys,
    encrypt_data_with_aes,
    decrypt_data_with_aes,
    encrypt_aes_key_with_rsa,
    decrypt_aes_key_with_rsa
)

from file_package_utils import (
    create_model_package,
    serialize_package,
    deserialize_package,
    restore_model_package,
    calculate_sha256
)

from mesh_utils import load_mesh
from evaluate import compare_mesh, compare_hash


MODEL_FILES = {
    "utah_teapot.obj": "models/utah_teapot.obj",
    "default.mtl": "models/default.mtl",
    "default.png": "models/default.png"
}

OUTPUT_MAPPING = {
    "utah_teapot.obj": "output/decrypted_utah_teapot.obj",
    "default.mtl": "output/default.mtl",
    "default.png": "output/default.png"
}

ORIGINAL_MODEL_PATH = "models/utah_teapot.obj"
DECRYPTED_MODEL_PATH = "output/decrypted_utah_teapot.obj"
ENCRYPTED_PATH = "output/encrypted_model.bin"

BENCHMARK_ROUNDS = 5


def average(values):
    return statistics.mean(values)


def main():
    os.makedirs("output", exist_ok=True)

    print("========== 3D Mesh Full Package Encryption Project ==========")
    print("Algorithm: Hybrid Cryptography AES-GCM + RSA-OAEP")
    print("Encrypted Data: OBJ + MTL + PNG")
    print(f"Benchmark Rounds: {BENCHMARK_ROUNDS}")

    # 1. Load original mesh for geometry information
    print("\n[1] Loading original 3D model for geometry check...")

    load_start = time.perf_counter()
    original_vertices, original_faces = load_mesh(ORIGINAL_MODEL_PATH)
    load_end = time.perf_counter()

    load_model_time = load_end - load_start

    print(f"Original Vertices: {len(original_vertices)}")
    print(f"Original Faces: {len(original_faces)}")
    print(f"Load Model Time: {load_model_time:.6f} seconds")

    # 2. Prepare time lists
    package_creation_times = []
    serialize_times = []

    aes_key_generation_times = []
    rsa_key_generation_times = []

    aes_encryption_times = []
    rsa_key_encryption_times = []

    rsa_key_decryption_times = []
    aes_decryption_times = []

    deserialize_times = []
    restore_file_times = []

    total_encryption_times = []
    total_decryption_times = []

    last_nonce = None
    last_encrypted_data = None
    last_encrypted_aes_key = None
    last_decrypted_package = None

    # 3. Run benchmark
    print(f"\n[2] Running encryption/decryption for {BENCHMARK_ROUNDS} rounds...")

    for round_no in range(1, BENCHMARK_ROUNDS + 1):
        print(f"\n---------- Round {round_no} ----------")

        # Encryption Process 1: Create model package
        package_start = time.perf_counter()
        model_package = create_model_package(MODEL_FILES)
        package_end = time.perf_counter()

        package_creation_time = package_end - package_start
        package_creation_times.append(package_creation_time)

        # Encryption Process 2: Serialize package to bytes
        serialize_start = time.perf_counter()
        package_bytes = serialize_package(model_package)
        serialize_end = time.perf_counter()

        serialize_time = serialize_end - serialize_start
        serialize_times.append(serialize_time)

        # Encryption Process 3: Generate AES key
        aes_key_start = time.perf_counter()
        aes_key = generate_aes_key()
        aes_key_end = time.perf_counter()

        aes_key_generation_time = aes_key_end - aes_key_start
        aes_key_generation_times.append(aes_key_generation_time)

        # Encryption Process 4: Generate RSA key pair
        rsa_key_start = time.perf_counter()
        rsa_private_key, rsa_public_key = generate_rsa_keys()
        rsa_key_end = time.perf_counter()

        rsa_key_generation_time = rsa_key_end - rsa_key_start
        rsa_key_generation_times.append(rsa_key_generation_time)

        # Encryption Process 5: AES encrypt full package
        aes_encrypt_start = time.perf_counter()
        nonce, encrypted_data = encrypt_data_with_aes(package_bytes, aes_key)
        aes_encrypt_end = time.perf_counter()

        aes_encryption_time = aes_encrypt_end - aes_encrypt_start
        aes_encryption_times.append(aes_encryption_time)

        # Encryption Process 6: RSA encrypt AES key
        rsa_encrypt_start = time.perf_counter()
        encrypted_aes_key = encrypt_aes_key_with_rsa(aes_key, rsa_public_key)
        rsa_encrypt_end = time.perf_counter()

        rsa_key_encryption_time = rsa_encrypt_end - rsa_encrypt_start
        rsa_key_encryption_times.append(rsa_key_encryption_time)

        total_encryption_time = (
            package_creation_time
            + serialize_time
            + aes_key_generation_time
            + rsa_key_generation_time
            + aes_encryption_time
            + rsa_key_encryption_time
        )

        total_encryption_times.append(total_encryption_time)

        # Decryption Process 1: RSA decrypt AES key
        rsa_decrypt_start = time.perf_counter()
        decrypted_aes_key = decrypt_aes_key_with_rsa(
            encrypted_aes_key,
            rsa_private_key
        )
        rsa_decrypt_end = time.perf_counter()

        rsa_key_decryption_time = rsa_decrypt_end - rsa_decrypt_start
        rsa_key_decryption_times.append(rsa_key_decryption_time)

        # Decryption Process 2: AES decrypt full package
        aes_decrypt_start = time.perf_counter()
        decrypted_package_bytes = decrypt_data_with_aes(
            nonce,
            encrypted_data,
            decrypted_aes_key
        )
        aes_decrypt_end = time.perf_counter()

        aes_decryption_time = aes_decrypt_end - aes_decrypt_start
        aes_decryption_times.append(aes_decryption_time)

        # Decryption Process 3: Deserialize package
        deserialize_start = time.perf_counter()
        decrypted_package = deserialize_package(decrypted_package_bytes)
        deserialize_end = time.perf_counter()

        deserialize_time = deserialize_end - deserialize_start
        deserialize_times.append(deserialize_time)

        # Decryption Process 4: Restore files to output folder
        restore_start = time.perf_counter()
        restore_model_package(decrypted_package, OUTPUT_MAPPING)
        restore_end = time.perf_counter()

        restore_file_time = restore_end - restore_start
        restore_file_times.append(restore_file_time)

        total_decryption_time = (
            rsa_key_decryption_time
            + aes_decryption_time
            + deserialize_time
            + restore_file_time
        )

        total_decryption_times.append(total_decryption_time)

        last_nonce = nonce
        last_encrypted_data = encrypted_data
        last_encrypted_aes_key = encrypted_aes_key
        last_decrypted_package = decrypted_package

        print("[Encryption Process]")
        print(f"Package Creation Time: {package_creation_time:.6f} seconds")
        print(f"Serialize Package Time: {serialize_time:.6f} seconds")
        print(f"AES Key Generation Time: {aes_key_generation_time:.6f} seconds")
        print(f"RSA Key Generation Time: {rsa_key_generation_time:.6f} seconds")
        print(f"AES Package Encryption Time: {aes_encryption_time:.6f} seconds")
        print(f"RSA AES-Key Encryption Time: {rsa_key_encryption_time:.6f} seconds")
        print(f"Total Encryption Time: {total_encryption_time:.6f} seconds")

        print("\n[Decryption Process]")
        print(f"RSA AES-Key Decryption Time: {rsa_key_decryption_time:.6f} seconds")
        print(f"AES Package Decryption Time: {aes_decryption_time:.6f} seconds")
        print(f"Deserialize Package Time: {deserialize_time:.6f} seconds")
        print(f"Restore Files Time: {restore_file_time:.6f} seconds")
        print(f"Total Decryption Time: {total_decryption_time:.6f} seconds")

    # 4. Save encrypted file from last round
    print("\n[3] Saving encrypted package from last round...")

    encrypted_package = {
        "algorithm": "Hybrid Cryptography AES-GCM + RSA-OAEP",
        "encrypted_files": list(MODEL_FILES.keys()),
        "nonce": last_nonce,
        "encrypted_data": last_encrypted_data,
        "encrypted_aes_key": last_encrypted_aes_key
    }

    with open(ENCRYPTED_PATH, "wb") as file:
        pickle.dump(encrypted_package, file)

    print(f"Encrypted file saved to: {ENCRYPTED_PATH}")
    print(f"Encrypted Package Data Size: {len(last_encrypted_data)} bytes")
    print(f"Encrypted AES Key Size: {len(last_encrypted_aes_key)} bytes")

    # 5. Load decrypted model for geometry comparison
    print("\n[4] Loading decrypted model for comparison...")

    decrypted_vertices, decrypted_faces = load_mesh(DECRYPTED_MODEL_PATH)

    print(f"Decrypted Vertices: {len(decrypted_vertices)}")
    print(f"Decrypted Faces: {len(decrypted_faces)}")

    # 6. Geometry error comparison
    print("\n[5] Comparing geometry error...")

    geometry_result = compare_mesh(
        original_vertices,
        original_faces,
        decrypted_vertices,
        decrypted_faces
    )

    # 7. File hash comparison
    print("\n[6] Comparing file hash integrity...")

    original_obj_hash = calculate_sha256("models/utah_teapot.obj")
    decrypted_obj_hash = calculate_sha256("output/decrypted_utah_teapot.obj")

    original_mtl_hash = calculate_sha256("models/default.mtl")
    decrypted_mtl_hash = calculate_sha256("output/default.mtl")

    original_png_hash = calculate_sha256("models/default.png")
    decrypted_png_hash = calculate_sha256("output/default.png")

    obj_hash_match = compare_hash(original_obj_hash, decrypted_obj_hash)
    mtl_hash_match = compare_hash(original_mtl_hash, decrypted_mtl_hash)
    png_hash_match = compare_hash(original_png_hash, decrypted_png_hash)

    # 8. Calculate average time
    avg_package_creation_time = average(package_creation_times)
    avg_serialize_time = average(serialize_times)

    avg_aes_key_generation_time = average(aes_key_generation_times)
    avg_rsa_key_generation_time = average(rsa_key_generation_times)

    avg_aes_encryption_time = average(aes_encryption_times)
    avg_rsa_key_encryption_time = average(rsa_key_encryption_times)

    avg_rsa_key_decryption_time = average(rsa_key_decryption_times)
    avg_aes_decryption_time = average(aes_decryption_times)

    avg_deserialize_time = average(deserialize_times)
    avg_restore_file_time = average(restore_file_times)

    avg_total_encryption_time = average(total_encryption_times)
    avg_total_decryption_time = average(total_decryption_times)

    # 9. Print geometry comparison result
    print("\n========== Geometry Error Comparison Result ==========")
    print(f"Original Vertices: {len(original_vertices)}")
    print(f"Decrypted Vertices: {len(decrypted_vertices)}")
    print(f"Original Faces: {len(original_faces)}")
    print(f"Decrypted Faces: {len(decrypted_faces)}")

    print(f"Vertex Count Difference: {geometry_result['vertex_count_diff']}")
    print(f"Face Count Difference: {geometry_result['face_count_diff']}")
    print(f"Mean Vertex Error: {geometry_result['mean_vertex_error']:.10f}")
    print(f"Max Vertex Error: {geometry_result['max_vertex_error']:.10f}")
    print(f"Face Mismatch: {geometry_result['face_mismatch']}")

    # 10. Print file integrity result
    print("\n========== File Integrity Hash Comparison Result ==========")
    print(f"OBJ Hash Match: {obj_hash_match}")
    print(f"MTL Hash Match: {mtl_hash_match}")
    print(f"PNG Hash Match: {png_hash_match}")

    if obj_hash_match and mtl_hash_match and png_hash_match:
        print("Result: Decrypted files are identical to the original files.")
    else:
        print("Result: Some decrypted files are different from the original files.")

    # 11. Print average encryption time
    print("\n========== Average Encryption Time Result ==========")
    print(f"Benchmark Rounds: {BENCHMARK_ROUNDS}")

    print(f"Average Package Creation Time: {avg_package_creation_time:.6f} seconds")
    print(f"Average Serialize Package Time: {avg_serialize_time:.6f} seconds")
    print(f"Average AES Key Generation Time: {avg_aes_key_generation_time:.6f} seconds")
    print(f"Average RSA Key Generation Time: {avg_rsa_key_generation_time:.6f} seconds")
    print(f"Average AES Package Encryption Time: {avg_aes_encryption_time:.6f} seconds")
    print(f"Average RSA AES-Key Encryption Time: {avg_rsa_key_encryption_time:.6f} seconds")
    print(f"Average Total Encryption Time: {avg_total_encryption_time:.6f} seconds")

    # 12. Print average decryption time
    print("\n========== Average Decryption Time Result ==========")
    print(f"Benchmark Rounds: {BENCHMARK_ROUNDS}")

    print(f"Average RSA AES-Key Decryption Time: {avg_rsa_key_decryption_time:.6f} seconds")
    print(f"Average AES Package Decryption Time: {avg_aes_decryption_time:.6f} seconds")
    print(f"Average Deserialize Package Time: {avg_deserialize_time:.6f} seconds")
    print(f"Average Restore Files Time: {avg_restore_file_time:.6f} seconds")
    print(f"Average Total Decryption Time: {avg_total_decryption_time:.6f} seconds")

    # 13. Compare encryption and decryption time
    print("\n========== Encryption vs Decryption Time Comparison ==========")
    print(f"Average Total Encryption Time: {avg_total_encryption_time:.6f} seconds")
    print(f"Average Total Decryption Time: {avg_total_decryption_time:.6f} seconds")

    time_difference = abs(avg_total_encryption_time - avg_total_decryption_time)

    print(f"Average Time Difference: {time_difference:.6f} seconds")

    if avg_total_encryption_time > avg_total_decryption_time:
        print("Result: Encryption process takes more average time than decryption process.")
    elif avg_total_decryption_time > avg_total_encryption_time:
        print("Result: Decryption process takes more average time than encryption process.")
    else:
        print("Result: Encryption and decryption take the same average time.")

    print("\n========== Output Files ==========")
    print("output/encrypted_model.bin")
    print("output/decrypted_utah_teapot.obj")
    print("output/default.mtl")
    print("output/default.png")

    print("\n========== Project Finished ==========")


if __name__ == "__main__":
    main()