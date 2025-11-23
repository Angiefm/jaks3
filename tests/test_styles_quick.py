"""test rapido de estilos"""
import sys
from pathlib import Path

# en este punto agrego la raiz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.image_generation.style_controller import (
    StyleController,
    DiagramType,
    ColorScheme,
    StyleConfig
)

print("=" * 60)
print("test: controlador de estilos (tarea 4)")
print("=" * 60)

controller = StyleController()

# aqui pruebo la auto sugerencia de estilos
print("\n1) auto sugerencia de estilos")
concepts = [
    "spring boot rest api architecture",
    "jpa entity relationships",
    "microservices communication flow",
    "spring security filter chain"
]

for concept in concepts:
    style = controller.suggest_style_for_concept(concept)
    print(f"\nconcepto: {concept}")
    print(f"   tipo: {style.diagram_type.value}")
    print(f"   colores: {style.color_scheme.value}")
    print(f"   complejidad: {style.complexity}")

# aqui genero prompts
print("\n\n2) generacion de prompts")
concept = "spring boot layered architecture"
style = controller.suggest_style_for_concept(concept)
prompt = controller.build_prompt(concept, style)
negative = controller.build_negative_prompt(style)

print(f"\nconcepto: {concept}")
print("\nprompt positivo:")
print(f"   {prompt[:150]}...")
print("\nprompt negativo:")
print(f"   {negative}")

# aqui reviso los presets disponibles
print("\n\n3) presets predefinidos")
for preset_name in controller.list_presets():
    preset = controller.get_preset(preset_name)
    print(f"\n{preset_name}")
    print(f"   tipo: {preset.diagram_type.value}")
    print(f"   colores: {preset.color_scheme.value}")
    print(f"   complejidad: {preset.complexity}")
    print(f"   layout: {preset.layout}")

# aqui genero variaciones de estilo
print("\n\n4) variaciones de estilo")
base_style = controller.suggest_style_for_concept("spring mvc pattern")
variations = controller.get_style_variations(base_style)

print("\nestilo base:")
print(f"   {base_style.diagram_type.value} | {base_style.color_scheme.value}")

print("\nvariaciones generadas:")
for i, var in enumerate(variations, 1):
    print(f"   {i}. {var.diagram_type.value} | {var.color_scheme.value} | {var.complexity}")

print("\ntest de estilos completado")
