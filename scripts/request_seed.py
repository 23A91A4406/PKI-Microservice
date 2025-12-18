import requests
import json

# Your details
student_id = "23A91A4406"
github_repo_url = "https://github.com/23A91A4406/2FA-PKI-Microservice"

# Read your public key
with open("student_public.pem", "r") as f:
    public_key_data = f.read()

# API endpoint
url = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/"

# Prepare request body
payload = {
    "student_id": student_id,
    "github_repo_url": github_repo_url,
    "public_key": public_key_data
}

try:
    print("Sending request to instructor API...")
    response = requests.post(url, json=payload)

    # Show status
    print("Status Code:", response.status_code)

    # Print server response
    print("Response Body:")
    print(response.text)

except Exception as e:
    print("Error contacting instructor API:", e)
