"""
módulo de generación de imágenes técnicas
aquí manejo el sistema completo con validación de calidad y fine-tuning
"""

__version__ = "1.0.0"

try:
    from .image_generator import ImageGenerator
except ImportError:
    ImageGenerator = None

try:
    from .image_quality_validator import ImageQualityValidator
except ImportError:
    ImageQualityValidator = None

try:
    from .style_controller import StyleController, DiagramType, ColorScheme, StyleConfig
except ImportError:
    StyleController = None
    DiagramType = None
    ColorScheme = None
    StyleConfig = None

try:
    from .finetuning_preparation import FineTuningPreparation
except ImportError:
    FineTuningPreparation = None

try:
    from .advanced_image_generator import AdvancedImageGenerator
except ImportError:
    AdvancedImageGenerator = None

# defino la lista de exports solo incluyo los que existen
__all__ = [
    name for name in [
        'ImageGenerator',
        'ImageQualityValidator',
        'StyleController',
        'DiagramType',
        'ColorScheme',
        'StyleConfig',
        'FineTuningPreparation',
        'AdvancedImageGenerator'
    ] if globals().get(name) is not None
]
