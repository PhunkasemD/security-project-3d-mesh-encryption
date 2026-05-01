import os
import time
import pickle
import statistics

from mesh_utils import load_mesh, save_mesh
from crypto_utils import (
    generate_aes_key,
    generate_rsa_keys,
    serialize_mesh,
    deserialize_mesh,
    encrypt_mesh_data,
    decrypt_mesh_data,
    encrypt_aes_key_with_rsa,
    decrypt_aes_key_with_rsa
)
from evaluate import compare_mesh


MODEL_PATH = "models/utah_teapot.obj"
ENCRYPTED_PATH = "output/encrypted_model.bin"
DECRYPTED_MODEL_PATH = "output/decrypted_utah_teapot.obj"

# รัน 5 รอบเพื่อดูค่าเฉลี่ยของเวลาในการเข้ารหัสและถอดรหัส
BENCHMARK_ROUNDS = 5


def average(values):
    return statistics.mean(values)


def main():
    os.makedirs("output", exist_ok=True)

    print("========== 3D Mesh Model Encryption Project ==========")
    print("Algorithm: Hybrid Cryptography AES-GCM + RSA-OAEP")
    print(f"Benchmark Rounds: {BENCHMARK_ROUNDS}")

    # 1. Load original 3D model
    print("\n[1] Loading original 3D model...")

    load_start = time.perf_counter()
    original_vertices, original_faces = load_mesh(MODEL_PATH)
    load_end = time.perf_counter()

    load_model_time = load_end - load_start

    print(f"Original Vertices: {len(original_vertices)}")
    print(f"Original Faces: {len(original_faces)}")
    print(f"Load Model Time: {load_model_time:.6f} seconds")

    # 2. Prepare time lists for benchmark
    serialize_times = []
    aes_key_generation_times = []
    rsa_key_generation_times = []

    aes_encryption_times = []
    rsa_key_encryption_times = []

    rsa_key_decryption_times = []
    aes_decryption_times = []

    deserialize_times = []

    total_encryption_times = []
    total_decryption_times = []

    # เก็บผลลัพธ์รอบสุดท้ายไว้ใช้บันทึกไฟล์และเปรียบเทียบ error
    last_nonce = None
    last_encrypted_data = None
    last_encrypted_aes_key = None
    last_decrypted_vertices = None
    last_decrypted_faces = None

    # 3. Run encryption/decryption benchmark
    print(f"\n[2] Running encryption/decryption for {BENCHMARK_ROUNDS} rounds...")

    for round_no in range(1, BENCHMARK_ROUNDS + 1):
        print(f"\n---------- Round {round_no} ----------")

        # Encryption Process 1: Serialize vertices/faces
        serialize_start = time.perf_counter()
        mesh_bytes = serialize_mesh(original_vertices, original_faces)
        serialize_end = time.perf_counter()

        serialize_time = serialize_end - serialize_start
        serialize_times.append(serialize_time)

        # Encryption Process 2: Generate AES key
        aes_key_start = time.perf_counter()
        aes_key = generate_aes_key()
        aes_key_end = time.perf_counter()

        aes_key_generation_time = aes_key_end - aes_key_start
        aes_key_generation_times.append(aes_key_generation_time)

        # Encryption Process 3: Generate RSA key pair
        rsa_key_start = time.perf_counter()
        rsa_private_key, rsa_public_key = generate_rsa_keys()
        rsa_key_end = time.perf_counter()

        rsa_key_generation_time = rsa_key_end - rsa_key_start
        rsa_key_generation_times.append(rsa_key_generation_time)

        # Encryption Process 4: AES encrypt mesh data
        aes_encrypt_start = time.perf_counter()
        nonce, encrypted_data = encrypt_mesh_data(mesh_bytes, aes_key)
        aes_encrypt_end = time.perf_counter()

        aes_encryption_time = aes_encrypt_end - aes_encrypt_start
        aes_encryption_times.append(aes_encryption_time)

        # Encryption Process 5: RSA encrypt AES key
        rsa_encrypt_start = time.perf_counter()
        encrypted_aes_key = encrypt_aes_key_with_rsa(aes_key, rsa_public_key)
        rsa_encrypt_end = time.perf_counter()

        rsa_key_encryption_time = rsa_encrypt_end - rsa_encrypt_start
        rsa_key_encryption_times.append(rsa_key_encryption_time)

        # เวลารวมของฝั่งเข้ารหัส
        total_encryption_time = (
            serialize_time
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

        # Decryption Process 2: AES decrypt mesh data
        aes_decrypt_start = time.perf_counter()
        decrypted_mesh_bytes = decrypt_mesh_data(
            nonce,
            encrypted_data,
            decrypted_aes_key
        )
        aes_decrypt_end = time.perf_counter()

        aes_decryption_time = aes_decrypt_end - aes_decrypt_start
        aes_decryption_times.append(aes_decryption_time)

        # Decryption Process 3: Deserialize bytes back to vertices/faces
        deserialize_start = time.perf_counter()
        decrypted_vertices, decrypted_faces = deserialize_mesh(decrypted_mesh_bytes)
        deserialize_end = time.perf_counter()

        deserialize_time = deserialize_end - deserialize_start
        deserialize_times.append(deserialize_time)

        # เวลารวมของฝั่งถอดรหัส
        total_decryption_time = (
            rsa_key_decryption_time
            + aes_decryption_time
            + deserialize_time
        )

        total_decryption_times.append(total_decryption_time)

        # เก็บผลรอบสุดท้ายไว้ใช้ต่อ
        last_nonce = nonce
        last_encrypted_data = encrypted_data
        last_encrypted_aes_key = encrypted_aes_key
        last_decrypted_vertices = decrypted_vertices
        last_decrypted_faces = decrypted_faces

        # Print time result of this round
        print("[Encryption Process]")
        print(f"Serialize Time: {serialize_time:.6f} seconds")
        print(f"AES Key Generation Time: {aes_key_generation_time:.6f} seconds")
        print(f"RSA Key Generation Time: {rsa_key_generation_time:.6f} seconds")
        print(f"AES Encryption Time: {aes_encryption_time:.6f} seconds")
        print(f"RSA AES-Key Encryption Time: {rsa_key_encryption_time:.6f} seconds")
        print(f"Total Encryption Time: {total_encryption_time:.6f} seconds")

        print("\n[Decryption Process]")
        print(f"RSA AES-Key Decryption Time: {rsa_key_decryption_time:.6f} seconds")
        print(f"AES Decryption Time: {aes_decryption_time:.6f} seconds")
        print(f"Deserialize Time: {deserialize_time:.6f} seconds")
        print(f"Total Decryption Time: {total_decryption_time:.6f} seconds")

    # 4. Save encrypted package from last round
    print("\n[3] Saving encrypted file from last round...")

    encrypted_package = {
        "algorithm": "Hybrid Cryptography AES-GCM + RSA-OAEP",
        "nonce": last_nonce,
        "encrypted_data": last_encrypted_data,
        "encrypted_aes_key": last_encrypted_aes_key
    }

    with open(ENCRYPTED_PATH, "wb") as file:
        pickle.dump(encrypted_package, file)

    print(f"Encrypted file saved to: {ENCRYPTED_PATH}")
    print(f"Encrypted Mesh Data Size: {len(last_encrypted_data)} bytes")
    print(f"Encrypted AES Key Size: {len(last_encrypted_aes_key)} bytes")

    # 5. Save decrypted model
    print("\n[4] Saving decrypted 3D model...")

    save_start = time.perf_counter()
    save_mesh(last_decrypted_vertices, last_decrypted_faces, DECRYPTED_MODEL_PATH)
    save_end = time.perf_counter()

    save_model_time = save_end - save_start

    print(f"Decrypted model saved to: {DECRYPTED_MODEL_PATH}")
    print(f"Save Decrypted Model Time: {save_model_time:.6f} seconds")

    # 6. Compare original and decrypted model
    print("\n[5] Comparing original model and decrypted model...")

    result = compare_mesh(
        original_vertices,
        original_faces,
        last_decrypted_vertices,
        last_decrypted_faces
    )

    # 7. Calculate average time
    avg_serialize_time = average(serialize_times)
    avg_aes_key_generation_time = average(aes_key_generation_times)
    avg_rsa_key_generation_time = average(rsa_key_generation_times)

    avg_aes_encryption_time = average(aes_encryption_times)
    avg_rsa_key_encryption_time = average(rsa_key_encryption_times)

    avg_rsa_key_decryption_time = average(rsa_key_decryption_times)
    avg_aes_decryption_time = average(aes_decryption_times)

    avg_deserialize_time = average(deserialize_times)

    avg_total_encryption_time = average(total_encryption_times)
    avg_total_decryption_time = average(total_decryption_times)

    # 8. Print final evaluation result
    print("\n========== Error Comparison Result ==========")
    print(f"Original Vertices: {len(original_vertices)}")
    print(f"Decrypted Vertices: {len(last_decrypted_vertices)}")
    print(f"Original Faces: {len(original_faces)}")
    print(f"Decrypted Faces: {len(last_decrypted_faces)}")

    print(f"Vertex Count Difference: {result['vertex_count_diff']}")
    print(f"Face Count Difference: {result['face_count_diff']}")
    print(f"Mean Vertex Error: {result['mean_vertex_error']:.10f}")
    print(f"Max Vertex Error: {result['max_vertex_error']:.10f}")
    print(f"Face Mismatch: {result['face_mismatch']}")

    # 9. Print average encryption time result
    print("\n========== Average Encryption Time Result ==========")
    print(f"Benchmark Rounds: {BENCHMARK_ROUNDS}")

    print(f"Average Serialize Time: {avg_serialize_time:.6f} seconds")
    print(f"Average AES Key Generation Time: {avg_aes_key_generation_time:.6f} seconds")
    print(f"Average RSA Key Generation Time: {avg_rsa_key_generation_time:.6f} seconds")
    print(f"Average AES Encryption Time: {avg_aes_encryption_time:.6f} seconds")
    print(f"Average RSA AES-Key Encryption Time: {avg_rsa_key_encryption_time:.6f} seconds")
    print(f"Average Total Encryption Time: {avg_total_encryption_time:.6f} seconds")

    # 10. Print average decryption time result
    print("\n========== Average Decryption Time Result ==========")
    print(f"Benchmark Rounds: {BENCHMARK_ROUNDS}")

    print(f"Average RSA AES-Key Decryption Time: {avg_rsa_key_decryption_time:.6f} seconds")
    print(f"Average AES Decryption Time: {avg_aes_decryption_time:.6f} seconds")
    print(f"Average Deserialize Time: {avg_deserialize_time:.6f} seconds")
    print(f"Average Total Decryption Time: {avg_total_decryption_time:.6f} seconds")

    # 11. Compare encryption and decryption time
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

    print("\n========== Project Finished ==========")


if __name__ == "__main__":
    main()