"""verifico api de stability ai"""
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

api_key = os.getenv("STABILITY_API_KEY")

print("="*60)
print("verificación de stability ai api")
print("="*60)

if not api_key:
    print("\nno se encontró stability_api_key en .env")
    exit(1)

print(f"\napi key encontrada: {api_key[:15]}...")

# verifico balance/cuenta
print("\n1. verificando cuenta...")
headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get(
    "https://api.stability.ai/v1/user/balance",
    headers=headers
)

print(f"   status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("   cuenta válida")
    print(f"   créditos: {data.get('credits', 'n/a')}")
else:
    print(f"   error: {response.text}")
    exit(1)

# verifico engin
