3D model reference: https://sketchfab.com/3d-models/the-utah-teapot-1092c2832df14099807f66c8b792374d

# 3D Mesh Model Encryption Project

This project demonstrates a security process for encrypting and decrypting a 3D mesh model using **Hybrid Cryptography: AES + RSA**.

The selected 3D model is **The Utah Teapot** in `.obj` format.  
The main mesh data used in this project are:

- **Vertices**: 3D coordinate points of the model
- **Faces**: surface information that connects vertices together

---

## Flow: Hybrid Encryption AES + RSA

The encryption and decryption process follows these steps:

1. Load the `teapot.obj` file
2. Extract `Vertices` and `Faces` from the 3D mesh model
3. Convert `Vertices` and `Faces` into bytes
4. Generate an AES Key
5. Use AES to encrypt the bytes of `Vertices` and `Faces`
6. Use the RSA Public Key to encrypt the AES Key
7. Save the encrypted result as `encrypted_model.bin`
8. Use the RSA Private Key to decrypt the AES Key
9. Use the AES Key to decrypt the encrypted 3D model data
10. Convert the decrypted bytes back into `Vertices` and `Faces`
11. Reconstruct and save the decrypted model as `decrypted_teapot.obj`
12. Compare the error and execution time between the original model and the decrypted model

---

## Process Overview

```text
Original 3D Model (.obj)
        ↓
Load teapot.obj
        ↓
Extract Vertices and Faces
        ↓
Convert Vertices/Faces to Bytes
        ↓
Generate AES Key
        ↓
AES Encryption for Mesh Data
        ↓
RSA Public Key Encryption for AES Key
        ↓
Save encrypted_model.bin
        ↓
RSA Private Key Decryption for AES Key
        ↓
AES Decryption for Mesh Data
        ↓
Convert Bytes back to Vertices/Faces
        ↓
Reconstruct decrypted_teapot.obj
        ↓
Compare Error and Time
