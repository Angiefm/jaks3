"""
script para probar el generador de imágenes
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import os
import logging
from dotenv import load_dotenv
from image_generation.image_generator import ImageGenerator

# cargo las variables de entorno
load_dotenv()

# configuro el logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_basic_generation():
    """ejecuto una prueba básica de generación"""
    print("=" * 60)
    print("test 1: generación básica")
    print("=" * 60)

    api_key = os.getenv("STABILITY_API_KEY")

    if not api_key:
        print("no encontré la api key para stability")
        return False

    print(f"api key detectada: {api_key[:10]}...")

    # inicializo el generador
    generator = ImageGenerator(api_key)

    # defino una consulta de prueba
    query = "Spring Boot MVC architecture diagram showing controller, service, and repository layers"
    print(f"query: {query}")

    # genero el prompt
    prompt = generator.text_to_prompt(query, style="architecture")
    print(f"prompt generado: {prompt}")

    # intento generar una imagen
    print("generando imagen...")
    result = generator.generate_from_query(query, style="architecture")

    if result["success"]:
        print("imagen generada correctamente")
        print(f"ruta: {result['path']}")
        print(f"tamaño: {result['size']}")
        return True
    else:
        print(f"error generando imagen: {result['error']}")
        return False


def test_multiple_styles():
    """muestro los estilos disponibles en el generador"""
    print("=" * 60)
    print("test 2: estilos disponibles")
    print("=" * 60)

    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        print("no encontré la api key; omito este test")
        return

    generator = ImageGenerator(api_key)

    print("estilos disponibles:")
    for style in generator.list_available_styles():
        description = generator.get_style_description(style)
        print(f"- {style}: {description}")


def test_batch_generation():
    """genero varias imágenes en lote"""
    print("=" * 60)
    print("test 3: generación en batch")
    print("=" * 60)

    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        print("no encontré la api key; omito este test")
        return

    generator = ImageGenerator(api_key)

    queries = [
        "Spring Security authentication flow diagram",
        "Microservices architecture with service discovery",
        "REST API request lifecycle in Spring Boot"
    ]

    print(f"voy a generar {len(queries)} imágenes")
    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")

    confirm = input("¿continuar? (s/n): ")
    if confirm.lower() != "s":
        print("test cancelado")
        return

    results = generator.batch_generate(queries, style="diagram")

    print("resultados:")
    for i, r in enumerate(results, 1):
        if r["success"]:
            print(f"{i}. generada en {r['path']}")
        else:
            print(f"{i}. error: {r.get('error', 'desconocido')}")


def test_prompt_conversion():
    """pruebo la conversión de texto a prompt"""
    print("=" * 60)
    print("test 4: conversión texto → prompt")
    print("=" * 60)

    api_key = os.getenv("STABILITY_API_KEY", "dummy")
    generator = ImageGenerator(api_key)

    queries = [
        "How does dependency injection work in Spring?",
        "Spring Boot REST API with JWT authentication",
        "Microservices communication patterns",
        "JPA entity relationship mapping",
        "Spring MVC request processing flow"
    ]

    for q in queries:
        prompt = generator.text_to_prompt(q, style="diagram")
        print(f"query: {q}")
        print(f"prompt: {prompt[:100]}...")
        print()


def main():
    """ejecuto todos los tests"""
    tests = [
        ("conversión texto a prompt", test_prompt_conversion),
        ("estilos disponibles", test_multiple_styles),
        ("generación básica", test_basic_generation),
        # descomento para probar generación en lote:
        # ("generación batch", test_batch_generation),
    ]

    for name, func in tests:
        try:
            func()
        except KeyboardInterrupt:
            print("interrumpí la ejecución")
            break
        except Exception as e:
            print(f"error en el test '{name}': {e}")
            import traceback
            traceback.print_exc()

    print("=" * 60)
    print("tests completados")
    print("=" * 60)


if __name__ == "__main__":
    main()
