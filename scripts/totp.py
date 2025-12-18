import time
import hmac
import hashlib
import struct
import os

SEED_FILE = "/data/seed.txt"


def load_seed_bytes():
    """
    Load hex seed from /data/seed.txt and convert to bytes
    """
    if not os.path.exists(SEED_FILE):
        raise FileNotFoundError("❌ seed.txt not found in /data folder")

    with open(SEED_FILE, "r") as f:
        hex_seed = f.read().strip()

    if len(hex_seed) != 64:
        raise ValueError("❌ Seed must be 64 hex characters")

    # 🔥 IMPORTANT FIX: hex string → bytes
    return bytes.fromhex(hex_seed)


def generate_totp_code():
    key = load_seed_bytes()   # BYTES ✔
    timestep = int(time.time()) // 30

    msg = struct.pack(">Q", timestep)
    hmac_hash = hmac.new(key, msg, hashlib.sha1).digest()

    offset = hmac_hash[-1] & 0x0F
    binary = struct.unpack(">I", hmac_hash[offset:offset + 4])[0] & 0x7fffffff
    code = binary % 1_000_000

    return f"{code:06d}"


def verify_totp_code(input_code):
    return generate_totp_code() == input_code


# Manual test
if __name__ == "__main__":
    code = generate_totp_code()
    remaining = 30 - (int(time.time()) % 30)
    print(f"Current TOTP code: {code}, valid for {remaining} seconds")
