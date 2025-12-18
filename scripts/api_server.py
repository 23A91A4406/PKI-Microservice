import sys
import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# Add scripts folder to Python path so we can import totp.py
sys.path.append(os.path.dirname(__file__))

from totp import generate_totp_code, verify_totp_code  # your totp functions

app = FastAPI()

# Path to seed file
SEED_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "seed.txt")
PRIVATE_KEY_PATH = os.path.join(os.path.dirname(__file__), "..", "student_private.pem")


# Pydantic models
class EncryptedSeedRequest(BaseModel):
    encrypted_seed: str

class VerifyCodeRequest(BaseModel):
    code: str


# Endpoint 1: POST /decrypt-seed
@app.post("/decrypt-seed")
def decrypt_seed_endpoint(request: EncryptedSeedRequest):
    try:
        # Load private key
        with open(PRIVATE_KEY_PATH, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)

        # Base64 decode
        encrypted_bytes = base64.b64decode(request.encrypted_seed)

        # RSA/OAEP-SHA256 decrypt
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        decrypted_seed = decrypted_bytes.decode("utf-8")

        # Validate 64-character hex
        if len(decrypted_seed) != 64 or not all(c in "0123456789abcdefABCDEF" for c in decrypted_seed):
            raise ValueError("Invalid seed format")

        # Save to seed.txt
        os.makedirs(os.path.dirname(SEED_FILE_PATH), exist_ok=True)
        with open(SEED_FILE_PATH, "w") as f:
            f.write(decrypted_seed)

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")


# Endpoint 2: GET /generate-2fa
@app.get("/generate-2fa")
def generate_2fa_endpoint():
    try:
        if not os.path.exists(SEED_FILE_PATH):
            raise ValueError("Seed not decrypted yet")

        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()

        code = generate_totp_code(hex_seed)

        # Calculate remaining seconds
        import time
        remaining = 30 - (int(time.time()) % 30)

        return {"code": code, "valid_for": remaining}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint 3: POST /verify-2fa
@app.post("/verify-2fa")
def verify_2fa_endpoint(request: VerifyCodeRequest):
    try:
        if not request.code:
            raise HTTPException(status_code=400, detail="Missing code")

        if not os.path.exists(SEED_FILE_PATH):
            raise HTTPException(status_code=500, detail="Seed not decrypted yet")

        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()

        valid = verify_totp_code(hex_seed, request.code)

        return {"valid": valid}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
