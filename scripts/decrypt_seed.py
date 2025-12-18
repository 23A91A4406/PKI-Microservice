import base64
import re
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


BASE_DIR = Path(__file__).resolve().parent.parent

ENCRYPTED_SEED_PATH = BASE_DIR / "encrypted_seed.txt"
PRIVATE_KEY_PATH = BASE_DIR / "student_private.pem"
OUTPUT_SEED_PATH = BASE_DIR / "seed.txt"


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64 encoded encrypted seed using RSA/OAEP (SHA-256)
    """

    # 1. Base64 decode
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    # 2. RSA OAEP decrypt
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 3. Decode bytes → string
    decrypted_seed = decrypted_bytes.decode("utf-8").strip()

    # 4. Validate 64-character hex string
    if len(decrypted_seed) != 64:
        raise ValueError("❌ Decrypted seed is not 64 characters long")

    if not re.fullmatch(r"[0-9a-fA-F]{64}", decrypted_seed):
        raise ValueError("❌ Decrypted seed is not a valid hexadecimal string")

    return decrypted_seed.lower()


def main():
    # Read encrypted seed
    if not ENCRYPTED_SEED_PATH.exists():
        raise FileNotFoundError("❌ encrypted_seed.txt not found in project root")

    encrypted_seed_b64 = ENCRYPTED_SEED_PATH.read_text().strip()

    # Load private key
    private_key = serialization.load_pem_private_key(
        PRIVATE_KEY_PATH.read_bytes(),
        password=None
    )

    # Decrypt
    seed = decrypt_seed(encrypted_seed_b64, private_key)

    # Save seed
    OUTPUT_SEED_PATH.write_text(seed)

    print("✅ Seed decrypted successfully!")
    print("🔑 Decrypted Seed:", seed)
    print("📁 Saved to seed.txt")


if __name__ == "__main__":
    main()
