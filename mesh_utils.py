import trimesh
import numpy as np


def load_mesh(file_path: str):
    """
    โหลดไฟล์ 3D Mesh Model แล้วดึง vertices และ faces ออกมา
    """
    mesh = trimesh.load(file_path, force="mesh")

    vertices = np.array(mesh.vertices, dtype=np.float64)
    faces = np.array(mesh.faces, dtype=np.int64)

    return vertices, faces