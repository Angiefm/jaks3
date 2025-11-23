"""
script para lanzar la demostración completa
tarea 5: demostración de mitad de curso
"""

import subprocess
import sys
from pathlib import Path
import os

def check_requirements():
    """verifico que todo esté listo"""
    print("verificando requisitos...")
    
    errors = []
    warnings = []
    
    # verifico la estructura del proyecto
    required_files = [
        "ui/main.py",
        "ui/pages/image_generation_page.py",
        "src/image_generation/advanced_image_generator.py",
        "src/image_generation/style_controller.py",
    ]
    
    for file in required_files:
        if not Path(file).exists():
            errors.append(f"falta archivo: {file}")
    
    # verifico las api keys
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("STABILITY_API_KEY"):
        warnings.append("STABILITY_API_KEY no está configurada (necesaria para generar imágenes)")
    
    if not os.getenv("GEMINI_API_KEY"):
        warnings.append("GEMINI_API_KEY no está configurada (necesaria para chat)")
    
    # verifico dependencias
    try:
        import streamlit
        import cv2
        from PIL import Image
    except ImportError as e:
        errors.append(f"dependencia faltante: {e}")
    
    # muestro resultados
    if errors:
        print("\nerrores encontrados:")
        for error in errors:
            print(f"  • {error}")
        return False
    
    if warnings:
        print("\nadvertencias:")
        for warning in warnings:
            print(f"  • {warning}")
    
    print("verificación completada\n")
    return True

def main():
    print("="*60)
    print("demostración - java api knowledge system")
    print("="*60)
    print("\ntarea 5: demostración de mitad de curso")
    print("\nmódulos disponibles:")
    print("  - chat rag con gemini")
    print("  - generador de imágenes técnicas")
    print("  - exploración visual de documentos")
    print("\n" + "="*60 + "\n")
    
    if not check_requirements():
        print("\nhay errores que deben corregirse antes de continuar")
        return 1
    
    print("iniciando streamlit...")
    print("\nla aplicación se abrirá en tu navegador")
    print("url: http://localhost:8501")
    print("\npresiona ctrl+c para detener\n")
    print("="*60 + "\n")
    
    # lanzo streamlit
    ui_path = Path(__file__).parent / "ui" / "main.py"
    
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ui_path),
            "--theme.base=light",
            "--theme.primaryColor=#7c3aed",
            "--theme.backgroundColor=#f3e8ff",
        ])
    except KeyboardInterrupt:
        print("\naplicación detenida")
        return 0

if __name__ == "__main__":
    exit(main())
