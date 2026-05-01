import numpy as np


def compare_mesh(original_vertices, original_faces, decrypted_vertices, decrypted_faces):
    """
    เปรียบเทียบ geometry ของโมเดลต้นฉบับกับโมเดลหลังถอดรหัส
    """

    vertex_count_diff = len(original_vertices) - len(decrypted_vertices)
    face_count_diff = len(original_faces) - len(decrypted_faces)

    vertex_error = np.abs(original_vertices - decrypted_vertices)

    mean_vertex_error = np.mean(vertex_error)
    max_vertex_error = np.max(vertex_error)

    face_mismatch = np.sum(original_faces != decrypted_faces)

    return {
        "vertex_count_diff": vertex_count_diff,
        "face_count_diff": face_count_diff,
        "mean_vertex_error": mean_vertex_error,
        "max_vertex_error": max_vertex_error,
        "face_mismatch": face_mismatch
    }


def compare_hash(original_hash, decrypted_hash):
    """
    เปรียบเทียบ hash ของไฟล์ต้นฉบับและไฟล์หลังถอดรหัส
    """
    return original_hash == decrypted_hash