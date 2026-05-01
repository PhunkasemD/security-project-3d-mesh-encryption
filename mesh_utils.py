import trimesh
import numpy as np


def load_mesh(file_path: str):
    """
    โหลดไฟล์ 3D Mesh Model แล้วดึงข้อมูล vertices และ faces ออกมา

    vertices = จุดพิกัดของโมเดล เช่น x, y, z
    faces = หน้าพื้นผิวที่เชื่อม vertices เข้าด้วยกัน
    """
    mesh = trimesh.load(file_path, force="mesh")

    vertices = np.array(mesh.vertices, dtype=np.float64)
    faces = np.array(mesh.faces, dtype=np.int64)

    return vertices, faces


def save_mesh(vertices, faces, output_path: str):
    """
    สร้างไฟล์ 3D Mesh Model กลับจาก vertices และ faces
    แล้ว export เป็นไฟล์ .obj
    """
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.export(output_path)