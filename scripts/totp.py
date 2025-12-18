import base64
import pyotp
import re


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed
    """

    # 1️⃣ Validate hex seed
    if len(hex_seed) != 64 or not re.fullmatch(r"[0-9a-fA-F]{64}", hex_seed):
        raise ValueError("Invalid hex seed format")

    # 2️⃣ Convert hex → bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # 3️⃣ Convert bytes → base32
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    # 4️⃣ Create TOTP object
    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30,
        digest="sha1"
    )

    # 5️⃣ Generate current TOTP
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with time window tolerance
    """

    # 1️⃣ Validate hex seed
    if len(hex_seed) != 64 or not re.fullmatch(r"[0-9a-fA-F]{64}", hex_seed):
        raise ValueError("Invalid hex seed format")

    # 2️⃣ Convert hex → bytes → base32
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    # 3️⃣ Create TOTP object
    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30,
        digest="sha1"
    )

    # 4️⃣ Verify code (± valid_window periods)
    return totp.verify(code, valid_window=valid_window)


# -------------------------------------------------
# OPTIONAL: Local test (you can delete later)
# -------------------------------------------------
from pathlib import Path

if __name__ == "__main__":
    # Bulletproof base directory
    BASE_DIR = Path(__file__).resolve().parent.parent
    SEED_PATH = BASE_DIR / "seed.txt"

    if not SEED_PATH.exists():
        raise FileNotFoundError("❌ seed.txt not found in project root")

    seed = SEED_PATH.read_text().strip()

    otp = generate_totp_code(seed)
    print("Generated TOTP:", otp)

    is_valid = verify_totp_code(seed, otp)
    print("Verification result:", is_valid)

