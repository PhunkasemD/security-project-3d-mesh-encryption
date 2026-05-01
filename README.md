3D model reference: https://sketchfab.com/3d-models/the-utah-teapot-1092c2832df14099807f66c8b792374d

# 3D Mesh Model Encryption Project

This project demonstrates a security process for encrypting and decrypting a 3D mesh model using **Hybrid Cryptography: AES + RSA**.

The selected 3D model is **The Utah Teapot**.  
In the latest version, this project encrypts the full model package, including:

- `utah_teapot.obj`: the main 3D mesh model file
- `default.mtl`: the material file
- `default.png`: the texture image file

This approach allows the decrypted output to be restored as closely as possible to the original model, including geometry, material, and texture.

---

## Main Data Used in This Project

The model package contains both geometry data and visual appearance data.

- **Vertices**: 3D coordinate points of the model
- **Faces**: surface information that connects vertices together
- **MTL file**: material information used by the OBJ model
- **PNG file**: texture image used by the material file

---

## Flow: Hybrid Encryption AES + RSA

The encryption and decryption process follows these steps:

1. Load the original model files: `utah_teapot.obj`, `default.mtl`, and `default.png`
2. Combine all model files into one model package
3. Convert the model package into bytes
4. Generate an AES Key
5. Generate an RSA Public Key and RSA Private Key
6. Use AES-GCM to encrypt the bytes of the model package
7. Use the RSA Public Key to encrypt the AES Key
8. Save the encrypted result as `encrypted_model.bin`
9. Use the RSA Private Key to decrypt the AES Key
10. Use the AES Key to decrypt the encrypted model package
11. Convert the decrypted bytes back into the original files
12. Restore the files as `decrypted_utah_teapot.obj`, `default.mtl`, and `default.png`
13. Compare the geometry error between the original model and the decrypted model
14. Compare the SHA-256 hash of the original files and the decrypted files
15. Compare the average encryption and decryption time from 5 benchmark rounds

---

## Process Overview

```text
Original Model Package
(utah_teapot.obj + default.mtl + default.png)
        ↓
Load Model Files
        ↓
Create Model Package
        ↓
Convert Model Package to Bytes
        ↓
Generate AES Key
        ↓
Generate RSA Public/Private Key
        ↓
AES-GCM Encryption for Model Package
        ↓
RSA Public Key Encryption for AES Key
        ↓
Save encrypted_model.bin
        ↓
RSA Private Key Decryption for AES Key
        ↓
AES-GCM Decryption for Model Package
        ↓
Convert Bytes Back to Original Files
        ↓
Restore decrypted_utah_teapot.obj + default.mtl + default.png
        ↓
Compare Geometry Error
        ↓
Compare SHA-256 File Hash
        ↓
Compare Average Encryption and Decryption Time
