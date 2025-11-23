"""verifico api de hugging face"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("STABILITY_API_KEY")

print("verificando api de hugging face...")
print(f"api key: {api_key[:15] if api_key else 'no encontrada'}...")

headers = {"Authorization": f"Bearer {api_key}"}

# verifico autenticación
print("\n1. verificando autenticación...")
response = requests.get("https://huggingface.co/api/whoami", headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"   autenticado como: {data.get('name', 'unknown')}")
else:
    print(f"   error {response.status_code}: {response.text}")
    exit(1)

# verifico acceso al modelo
print("\n2. verificando acceso al modelo...")
model_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

test_payload = {
    "inputs": "a technical diagram"
}

response = requests.post(model_url, headers=headers, json=test_payload, timeout=10)

print(f"   status: {response.status_code}")

if response.status_code == 200:
    print("   modelo accesible")
elif response.status_code == 503:
    print("   modelo cargando (normal en primera vez)")
else:
    print(f"   error: {response.text[:200]}")

print("\n" + "="*60)
