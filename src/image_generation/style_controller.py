"""
Controlador avanzado de estilos para generación de imágenes
Permite control fino sobre aspectos visuales
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DiagramType(Enum):
    """Tipos de diagramas soportados"""
    UML_CLASS = "uml_class"
    SEQUENCE = "sequence"
    ARCHITECTURE = "architecture"
    FLOWCHART = "flowchart"
    ER_DIAGRAM = "er_diagram"
    COMPONENT = "component"
    DEPLOYMENT = "deployment"
    STATE_MACHINE = "state_machine"


class ColorScheme(Enum):
    """Esquemas de color disponibles"""
    PROFESSIONAL = "professional"  
    VIBRANT = "vibrant"            
    MONOCHROME = "monochrome"      
    PASTEL = "pastel"              
    DARK_MODE = "dark_mode"        
    SPRING_THEMED = "spring_themed"


@dataclass
class StyleConfig:
    """Configuración completa de estilo"""
    diagram_type: DiagramType
    color_scheme: ColorScheme
    complexity: str
    layout: str    
    emphasis: str  
    background: str


class StyleController:
    """
    Controlador avanzado de estilos.
    Genera prompts optimizados para generación de diagramas técnicos.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Templates base por tipo de diagrama
        self.diagram_templates = {
            DiagramType.UML_CLASS: "UML class diagram, boxes with attributes and methods, inheritance arrows, clean object-oriented design",
            DiagramType.SEQUENCE: "UML sequence diagram, vertical lifelines, horizontal messages, time flowing downward",
            DiagramType.ARCHITECTURE: "system architecture diagram, layers and components, clear connections, high-level view",
            DiagramType.FLOWCHART: "flowchart diagram, decision nodes, process boxes, directional arrows, sequential flow",
            DiagramType.ER_DIAGRAM: "entity relationship diagram, tables with columns, relationship lines, database schema",
            DiagramType.COMPONENT: "component diagram, modular boxes, interface connections, system decomposition",
            DiagramType.DEPLOYMENT: "deployment diagram, nodes and artifacts, hardware and software mapping",
            DiagramType.STATE_MACHINE: "state machine diagram, states as circles, transitions as arrows, events labeled"
        }

        # Esquemas de color
        self.color_schemes = {
            ColorScheme.PROFESSIONAL: "professional blue and gray color palette, corporate style, clean colors",
            ColorScheme.VIBRANT: "vibrant colors, high saturation, eye-catching palette, modern look",
            ColorScheme.MONOCHROME: "black and white, grayscale, no colors, high contrast",
            ColorScheme.PASTEL: "soft pastel colors, light tones, gentle palette, soothing colors",
            ColorScheme.DARK_MODE: "dark background, light text, dark theme, modern dark UI",
            ColorScheme.SPRING_THEMED: "Spring Framework colors, green and orange accents, branded palette"
        }

        # Complejidad
        self.complexity_modifiers = {
            'simple': "simple, minimal elements, basic representation, easy to understand",
            'medium': "moderate detail, balanced complexity, clear but informative",
            'detailed': "highly detailed, comprehensive, many elements, thorough representation"
        }

        # Layouts
        self.layout_modifiers = {
            'vertical': "vertical layout, top-to-bottom flow, stacked arrangement",
            'horizontal': "horizontal layout, left-to-right flow, side-by-side arrangement",
            'circular': "circular layout, radial arrangement, center-outward design",
            'grid': "grid layout, matrix arrangement, organized in rows and columns"
        }

        # Énfasis
        self.emphasis_modifiers = {
            'minimalist': "minimalist design, clean lines, sparse elements, focus on essentials",
            'detailed': "detailed annotations, explanatory labels, comprehensive information",
            'annotated': "well annotated, descriptive labels, explanatory text, tutorial style"
        }

        # Fondos
        self.background_modifiers = {
            'white': "white background, clean backdrop, high contrast",
            'transparent': "transparent background, no backdrop",
            'gradient': "subtle gradient background, professional look"
        }

        self.logger.info("StyleController inicializado")

    def build_prompt(self, technical_concept: str, style_config: StyleConfig) -> str:
        """
        Construye prompt completo basado en una configuración de estilo.
        """
        components = [
            technical_concept,
            self.diagram_templates[style_config.diagram_type],
            self.color_schemes[style_config.color_scheme],
            self.complexity_modifiers[style_config.complexity],
            self.layout_modifiers[style_config.layout],
            self.emphasis_modifiers[style_config.emphasis],
            self.background_modifiers[style_config.background],
            "high quality, professional rendering, technical illustration, clear and precise"
        ]

        prompt = ", ".join(components)
        self.logger.info(f"Prompt construido para {style_config.diagram_type.value}")
        return prompt

    def build_negative_prompt(self, style_config: StyleConfig) -> str:
        """
        Construye negative prompt específico según configuración.
        """
        negative = [
            "distorted text", "garbled text", "unreadable text", 
            "mixed languages", "random characters", "corrupted letters",
            "blurry text", "overlapping text", "scrambled words",
            "nonsense text", "gibberish", "mangled typography",
            "photo", "photograph", "realistic", "3d render",
            "low quality", "blurry", "pixelated", "watermark"
        ]

        if style_config.diagram_type in [DiagramType.UML_CLASS, DiagramType.ER_DIAGRAM]:
            negative.extend(["curved lines", "artistic", "decorative"])

        if style_config.color_scheme == ColorScheme.MONOCHROME:
            negative.append("colors")

        if style_config.emphasis == 'minimalist':
            negative.extend(["cluttered", "too much text", "overcrowded"])

        if style_config.background == 'white':
            negative.extend(["dark background", "colored background"])

        return ", ".join(negative)

    def suggest_style_for_concept(self, technical_concept: str) -> StyleConfig:
        """
        Sugiere estilo óptimo basado en el concepto técnico.
        """
        concept = technical_concept.lower()

        # Tipo de diagrama
        if any(w in concept for w in ['class', 'object', 'inheritance', 'interface']):
            diag = DiagramType.UML_CLASS
        elif any(w in concept for w in ['sequence', 'interaction', 'message']):
            diag = DiagramType.SEQUENCE
        elif any(w in concept for w in ['architecture', 'system', 'layer']):
            diag = DiagramType.ARCHITECTURE
        elif any(w in concept for w in ['flow', 'process', 'algorithm']):
            diag = DiagramType.FLOWCHART
        elif any(w in concept for w in ['database', 'entity', 'table', 'relationship']):
            diag = DiagramType.ER_DIAGRAM
        elif any(w in concept for w in ['component', 'module']):
            diag = DiagramType.COMPONENT
        else:
            diag = DiagramType.ARCHITECTURE

        # Colores
        color = ColorScheme.SPRING_THEMED if 'spring' in concept else ColorScheme.PROFESSIONAL

        # Complejidad
        if any(w in concept for w in ['simple', 'basic', 'intro']):
            complex_lvl = 'simple'
        elif any(w in concept for w in ['detailed', 'complete', 'comprehensive']):
            complex_lvl = 'detailed'
        else:
            complex_lvl = 'medium'

        return StyleConfig(
            diagram_type=diag,
            color_scheme=color,
            complexity=complex_lvl,
            layout='vertical',
            emphasis='detailed',
            background='white'
        )

    def get_style_variations(self, base: StyleConfig) -> List[StyleConfig]:
        """Genera variaciones del estilo base."""
        return [
            StyleConfig(
                diagram_type=base.diagram_type,
                color_scheme=ColorScheme.MONOCHROME,
                complexity=base.complexity,
                layout=base.layout,
                emphasis=base.emphasis,
                background=base.background
            ),
            StyleConfig(
                diagram_type=base.diagram_type,
                color_scheme=base.color_scheme,
                complexity='simple' if base.complexity != 'simple' else 'detailed',
                layout=base.layout,
                emphasis=base.emphasis,
                background=base.background
            ),
            StyleConfig(
                diagram_type=base.diagram_type,
                color_scheme=base.color_scheme,
                complexity=base.complexity,
                layout='horizontal' if base.layout == 'vertical' else 'vertical',
                emphasis=base.emphasis,
                background=base.background
            ),
        ]

    def get_preset(self, name: str) -> Optional[StyleConfig]:
        """Obtiene un preset de estilo."""
        presets = {
            'tutorial': StyleConfig(
                diagram_type=DiagramType.ARCHITECTURE,
                color_scheme=ColorScheme.PASTEL,
                complexity='simple',
                layout='vertical',
                emphasis='annotated',
                background='white'
            ),
            'presentation': StyleConfig(
                diagram_type=DiagramType.ARCHITECTURE,
                color_scheme=ColorScheme.VIBRANT,
                complexity='medium',
                layout='horizontal',
                emphasis='minimalist',
                background='gradient'
            ),
            'documentation': StyleConfig(
                diagram_type=DiagramType.ARCHITECTURE,
                color_scheme=ColorScheme.PROFESSIONAL,
                complexity='detailed',
                layout='grid',
                emphasis='detailed',
                background='white'
            ),
            'spring_official': StyleConfig(
                diagram_type=DiagramType.ARCHITECTURE,
                color_scheme=ColorScheme.SPRING_THEMED,
                complexity='medium',
                layout='vertical',
                emphasis='detailed',
                background='white'
            )
        }
        return presets.get(name)

    def list_presets(self) -> List[str]:
        """Lista presets disponibles."""
        return ['tutorial', 'presentation', 'documentation', 'spring_official']


# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    controller = StyleController()

    concept = "Spring Boot REST API architecture with controller service repository pattern"
    suggested = controller.suggest_style_for_concept(concept)

    print("Concepto:", concept)
    print("\nEstilo sugerido:")
    print(f"  Tipo: {suggested.diagram_type.value}")
    print(f"  Colores: {suggested.color_scheme.value}")
    print(f"  Complejidad: {suggested.complexity}")

    prompt = controller.build_prompt(concept, suggested)
    negative = controller.build_negative_prompt(suggested)

    print(f"\nPrompt generado:\n{prompt[:150]}...\n")
    print(f"Negative prompt:\n{negative}")

    print("\nPresets disponibles:")
    for preset in controller.list_presets():
        print(f"  • {preset}")
