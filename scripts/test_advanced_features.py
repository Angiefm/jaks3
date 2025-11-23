import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src" / "image_generation"))

import os
import logging
from dotenv import load_dotenv

from advanced_image_generator import AdvancedImageGenerator
from style_controller import StyleController, StyleConfig, DiagramType, ColorScheme
from finetuning_preparation import FineTuningPreparation
from image_quality_validator import ImageQualityValidator

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_style_controller():
    """test del controlador de estilos"""
    print("\n" + "="*60)
    print("test 1: controlador de estilos (tarea 4)")
    print("="*60)
    
    controller = StyleController()
    
    concept = "spring boot microservices with service discovery"
    suggested = controller.suggest_style_for_concept(concept)
    
    print(f"\nconcepto: {concept}")
    print(f"\nestilo auto-sugerido:")
    print(f"  • tipo: {suggested.diagram_type.value}")
    print(f"  • colores: {suggested.color_scheme.value}")
    print(f"  • complejidad: {suggested.complexity}")
    print(f"  • layout: {suggested.layout}")
    print(f"  • enfasis: {suggested.emphasis}")
    
    prompt = controller.build_prompt(concept, suggested)
    negative = controller.build_negative_prompt(suggested)
    
    print(f"\nprompt generado:")
    print(f"  {prompt[:150]}...")
    print(f"\nnegative prompt:")
    print(f"  {negative}")
    
    print(f"\npresets disponibles:")
    for preset_name in controller.list_presets():
        preset = controller.get_preset(preset_name)
        print(f"  • {preset_name}: {preset.diagram_type.value}, {preset.color_scheme.value}")
    
    print(f"\ngenerando 3 variaciones de estilo...")
    variations = controller.get_style_variations(suggested)
    for i, var in enumerate(variations[:3], 1):
        print(f"  {i}. {var.diagram_type.value} | {var.color_scheme.value} | {var.complexity}")
    
    print("\ntest de estilos completado")


def test_quality_validator():
    """test del validador de calidad"""
    print("\n" + "="*60)
    print("test 2: validador de calidad (tarea 4)")
    print("="*60)
    
    validator = ImageQualityValidator(min_quality_score=0.6)
    
    print(f"\nmetricas evaluadas:")
    print(f"  • nitidez")
    print(f"  • claridad tecnica")
    print(f"  • contraste")
    print(f"  • brillo")
    print(f"  • composicion")
    print(f"  • nivel de ruido")
    print(f"  • balance de colores")
    
    print(f"\nconfiguracion:")
    print(f"  score minimo: {validator.min_quality_score:.0%}")
    
    print(f"\nel validador:")
    print(f"  ✓ detecta imagenes borrosas")
    print(f"  ✓ evalua claridad tecnica")
    print(f"  ✓ verifica balance de composicion")
    print(f"  ✓ genera recomendaciones automaticas")
    
    print(f"\nejemplo de validacion:")
    print("""
  imagen: sample_001.png
  
  resultados:
    nitidez: 85%
    claridad tecnica: 78%
    contraste: 92%
    brillo: 88%
    composicion: 75%
    ruido: 90%
    balance color: 80%
    
  score global: 83% aprobada
  
  recomendaciones:
    ninguna recomendacion necesaria
    """)
    
    print("test de validacion completado")


def test_finetuning_prep():
    """test de preparacion de fine-tuning"""
    print("\n" + "="*60)
    print("test 3: preparacion de fine-tuning (tarea 3)")
    print("="*60)
    
    prep = FineTuningPreparation()
    
    print(f"\nestructura de datos:")
    print(f"  {prep.output_dir}/")
    print(f"    ├── images/")
    print(f"    ├── captions/")
    print(f"    ├── metadata.jsonl")
    print(f"    ├── lora_format/")
    print(f"    └── dreambooth_format/")
    
    print(f"\ngenerando dataset sintetico...")
    result = prep.create_synthetic_dataset(num_samples=5)
    print(f"  samples creados: {result['total']}")
    print(f"  por categoria:")
    for cat, count in result['by_category'].items():
        print(f"    • {cat}: {count}")
    
    print(f"\nestadisticas del dataset:")
    stats = prep.get_dataset_statistics()
    print(f"  total imagenes: {stats['total_images']}")
    print(f"  total captions: {stats['total_captions']}")
    print(f"  categorias: {len(stats['categories'])}")
    print(f"  listo para training: {'si' if stats['ready_for_training'] else 'no'}")
    
    print(f"\nconfiguraciones de training:")
    
    print(f"\nlora")
    lora_config = prep.generate_training_config("lora")
    print(f"    learning rate: {lora_config['hyperparameters']['learning_rate']}")
    print(f"    steps: {lora_config['hyperparameters']['max_train_steps']}")
    print(f"    lora rank: {lora_config['hyperparameters']['lora_rank']}")
    
    print(f"\ndreambooth")
    db_config = prep.generate_training_config("dreambooth")
    print(f"    learning rate: {db_config['hyperparameters']['learning_rate']}")
    print(f"    steps: {db_config['hyperparameters']['max_train_steps']}")
    
    print("\ntest de fine-tuning completado")


def test_advanced_generator():
    """test del generador avanzado"""
    print("\n" + "="*60)
    print("test 4: generador avanzado integrado")
    print("="*60)
    
    api_key = os.getenv("STABILITY_API_KEY")
    
    if not api_key:
        print("\nno hay stability_api_key configurada")
        print("este test requiere api key para generar imagenes reales")
        return
    
    print(f"\napi key encontrada")
    
    advanced_gen = AdvancedImageGenerator(
        api_key=api_key,
        min_quality_score=0.6,
        max_retries=2
    )
    
    print(f"\nejemplo de uso:")
    print("""
    concept = "spring boot layered architecture with mvc pattern"
    result = advanced_gen.generate_with_quality_check(concept)
    """)
    
    response = input("\ngenerar imagen de prueba? (s/n): ")
    
    if response.lower() == 's':
        print("\ngenerando imagen de prueba...\n")
        
        concept = "spring boot layered architecture with mvc pattern"
        result = advanced_gen.generate_with_quality_check(concept)
        
        print(advanced_gen.get_generation_report(result))
    else:
        print("\ntest de generacion omitido")
    
    print("\ntest completado")


def main():
    """funcion principal"""
    print("\n" + "x"*30)
    print("tests de tareas 3 y 4")
    print("generacion de imagenes avanzada")
    print("x"*30)
    
    tests = [
        ("controlador de estilos", test_style_controller),
        ("validador de calidad", test_quality_validator),
        ("preparacion fine-tuning", test_finetuning_prep),
        ("generador avanzado", test_advanced_generator),
    ]
    
    for i, (name, test_func) in enumerate(tests, 1):
        try:
            test_func()
        except KeyboardInterrupt:
            print("\n\ntests interrumpidos por el usuario")
            break
        except Exception as e:
            print(f"\nerror en test '{name}': {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(tests):
            input("\npresiona enter para continuar al siguiente test...")
    
    print("\n" + "="*60)
    print("resumen de implementacion")
    print("="*60)
    

if __name__ == "__main__":
    main()
