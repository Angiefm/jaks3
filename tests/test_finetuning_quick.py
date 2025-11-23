"""test rapido de fine-tuning"""
import sys
from pathlib import Path

# aseguro que src esté en el path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.image_generation.finetuning_preparation import finetuningpreparation

print("="*60)
print("test: preparación de fine-tuning (tarea 3)")
print("="*60)

prep = finetuningpreparation()

# test 1: estructura de directorios
print("\n1  estructura de datos")
print(f"\n directorio base: {prep.output_dir}")
print(f"   ├── images/       {'si' if prep.images_dir.exists() else 'no'}")
print(f"   ├── captions/     {'si' if prep.captions_dir.exists() else 'no'}")
print(f"   └── metadata.jsonl")

# test 2: generación de captions
print("\n\n2  generación de captions")
conceptos = [
    ("spring boot architecture", "architecture"),
    ("jpa entity mapping", "uml"),
    ("request processing flow", "flowchart")
]

for concepto, categoria in conceptos:
    variaciones = prep.generate_caption_variations(concepto, categoria, num_variations=2)
    print(f"\n {concepto} ({categoria}):")
    for i, v in enumerate(variaciones, 1):
        print(f"   {i}. {v[:80]}...")

# test 3: dataset sintético
print("\n\n3  creación de dataset sintético")
resultado = prep.create_synthetic_dataset(num_samples=5)
print(f"\n samples creados: {resultado['total']}")
print(f"   por categoría:")
for cat, count in resultado['by_category'].items():
    print(f"     • {cat}: {count}")

# test 4: estadísticas
print("\n\n4  estadísticas del dataset")
estadisticas = prep.get_dataset_statistics()
print(f"\n   total imágenes: {estadisticas['total_images']}")
print(f"   total captions: {estadisticas['total_captions']}")
print(f"   categorías: {len(estadisticas['categories'])}")
print(f"   listo para training: {'si' if estadisticas['ready_for_training'] else 'no'}")

# test 5: configuraciones de training
print("\n\n5  configuraciones de training")

print("\n lora config:")
config_lora = prep.generate_training_config("lora")
print(f"   • learning rate: {config_lora['hyperparameters']['learning_rate']}")
print(f"   • max steps: {config_lora['hyperparameters']['max_train_steps']}")
print(f"   • lora rank: {config_lora['hyperparameters']['lora_rank']}")

print("\n dreambooth config:")
config_db = prep.generate_training_config("dreambooth")
print(f"   • learning rate: {config_db['hyperparameters']['learning_rate']}")
print(f"   • max steps: {config_db['hyperparameters']['max_train_steps']}")

print("\n test de fine-tuning completado")
print(f"\n archivos guardados en: {prep.output_dir}")
