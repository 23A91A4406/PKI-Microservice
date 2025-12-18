import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


# ---------- CONFIG ----------
COMMIT_HASH = "89ae1fd7dba8a8a0d3c31079e6fa9a57350b00e4"
STUDENT_PRIVATE_KEY_FILE = "student_private.pem"
INSTRUCTOR_PUBLIC_KEY_FILE = "instructor_public.pem"
# ----------------------------


def load_private_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )


def load_public_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )


def sign_message(message: str, private_key) -> bytes:
    return private_key.sign(
        message.encode("utf-8"),   # CRITICAL
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def main():
    private_key = load_private_key(STUDENT_PRIVATE_KEY_FILE)
    instructor_public_key = load_public_key(INSTRUCTOR_PUBLIC_KEY_FILE)

    signature = sign_message(COMMIT_HASH, private_key)
    encrypted_signature = encrypt_with_public_key(signature, instructor_public_key)

    encoded = base64.b64encode(encrypted_signature).decode("utf-8")

    print("\n✅ COMMIT PROOF GENERATED\n")
    print("Commit Hash:")
    print(COMMIT_HASH)
    print("\nEncrypted Signature (Base64):")
    print(encoded)


if __name__ == "__main__":
    main()
