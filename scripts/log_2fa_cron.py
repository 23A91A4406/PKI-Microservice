#!/usr/bin/env python3

import time
from totp import generate_totp_code

LOG_FILE = "/cron/last_code.txt"

code = generate_totp_code()
timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

with open(LOG_FILE, "a") as f:
    f.write(f"{timestamp} - 2FA Code: {code}\n")

print(f"✅ Logged TOTP: {code} at {timestamp}")
