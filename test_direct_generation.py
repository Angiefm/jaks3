"""test directo del generador de imágenes - stability ai"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

from src.image_generation.image_generator import ImageGenerator

print("="*60)
print("test directo de generación - stability ai")
print("="*60)

# uso stability_api_key en lugar de huggingface_api_key
api_key = os.getenv("STABILITY_API_KEY")

if not api_key:
    print("\nno se encontró stability_api_key en .env")
    print("\npasos para configurarla:")
    print("1. ir a https://stability.ai")
    print("2. crear cuenta y obtener la api key")
    print("3. agregarla a .env:")
    print("   STABILITY_API_KEY=sk-tu_key_aqui")
    exit(1)

print(f"\napi key: {api_key[:15]}...")

# test 1: inicialización
print("\n1. inicializando generador...")
try:
    generator = ImageGenerator(api_key)
    print("   generador creado")
except Exception as e:
    print(f"   error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# test 2: conversión de texto a prompt
print("\n2. probando conversión de texto a prompt...")
try:
    concept = "Spring Boot REST API architecture"
    prompt = generator.text_to_prompt(concept, style="architecture")
    print("   prompt generado:")
    print(f"      {prompt[:100]}...")
except Exception as e:
    print(f"   error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# test 3: generación real
print("\n3. intentando generar imagen...")
print("   esto tomará 20-30 segundos...")
print("   se consumirán aproximadamente 0.02 créditos de stability ai")

try:
    result = generator.generate_from_query(
        "Spring Boot REST API with controller service repository",
        style="architecture"
    )
    
    print("\nresultado:")
    print(f"   success: {result.get('success')}")
    
    if result.get('success'):
        print(f"   imagen generada: {result['path']}")
        print(f"   tamaño: {result.get('size')}")
        print("   ubicación: data/generated_images/")
        print("\nabre la imagen para ver el resultado")
    else:
        print(f"   error: {result.get('error', 'unknown')}")
        print("\nposibles causas:")
        print("   • api key inválida")
        print("   • sin créditos suficientes")
        print("   • problema de red")
        print("\nverifica con: python test_stability_api.py")
        
except Exception as e:
    print(f"\nexcepción: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
