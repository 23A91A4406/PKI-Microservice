#!/usr/bin/env python3
# Cron script to log 2FA codes every minute

import os
import time
from totp import generate_totp_code  # import your corrected totp function

SEED_FILE = "/data/seed.txt"
LOG_FILE = "/cron/last_code.txt"

# Read hex seed
try:
    with open(SEED_FILE, "r") as f:
        hex_seed = f.read().strip()
except FileNotFoundError:
    print("❌ seed.txt not found in /data folder")
    exit(1)

# Generate TOTP code
try:
    code = generate_totp_code(hex_seed)
except Exception as e:
    print(f"❌ Error generating TOTP: {e}")
    exit(1)

# Get current UTC timestamp
timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

# Append to log file (creates file if it doesn't exist)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
with open(LOG_FILE, "a") as f:
    f.write(f"{timestamp} - 2FA Code: {code}\n")

print(f"✅ Logged TOTP: {code} at {timestamp}")
