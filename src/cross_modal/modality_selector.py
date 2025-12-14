from typing import List, Dict, Optional  
from enum import Enum  

class ModalityType(Enum):  
    TEXT_ONLY = "text_only"  
    IMAGE_ONLY = "image_only"  
    TEXT_AND_IMAGE = "text_and_image"  

class ModalitySelector:  
    """  
    selecciona la modalidad adecuada basada en el análisis del contenido  
    """  

    def __init__(self):  
        self.visual_keywords = [  
            'arquitectura', 'diagrama', 'flujo', 'estructura',  
            'componentes', 'capas', 'mvc', 'rest', 'api',  
            'patrón', 'diseño', 'esquema', 'visual'  
        ]  

        self.complexity_indicators = [  
            'complejo', 'múltiple', 'integración', 'sistema',  
            'arquitectura completa', 'end-to-end'  
        ]  

    def select_modality(self, question: str, context_sources: List[Dict] = None) -> ModalityType:  
        """  
        selecciona modalidad basada en pregunta y contexto  
        """  
        question_lower = question.lower()  

        # contar keywords visuales  
        visual_score = sum(1 for keyword in self.visual_keywords   
                          if keyword in question_lower)  

        # evaluar complejidad  
        complexity_score = sum(1 for indicator in self.complexity_indicators   
                             if indicator in question_lower)  

        # analizar contexto si está disponible  
        context_visual_score = 0  
        if context_sources:  
            for source in context_sources:  
                source_text = str(source.get('content', '')).lower()  
                context_visual_score += sum(1 for keyword in self.visual_keywords   
                                          if keyword in source_text)  

        # decisión final  
        total_visual_score = visual_score + (context_visual_score / len(context_sources) if context_sources else 0)  

        if total_visual_score >= 2 or complexity_score >= 2:  
            return ModalityType.TEXT_AND_IMAGE  
        elif total_visual_score >= 1:  
            return ModalityType.IMAGE_ONLY  
        else:  
            return ModalityType.TEXT_ONLY  

    def get_modality_confidence(self, question: str, modality: ModalityType) -> float:  
        """  
        calcula confianza en la selección de modalidad (0.0 - 1.0)  
        """  
        question_lower = question.lower()  

        if modality == ModalityType.TEXT_AND_IMAGE:  
            keyword_matches = sum(1 for keyword in self.visual_keywords   
                                if keyword in question_lower)  
            return min(keyword_matches / 3.0, 1.0)  

        elif modality == ModalityType.IMAGE_ONLY:  
            keyword_matches = sum(1 for keyword in self.visual_keywords   
                                if keyword in question_lower)  
            return min(keyword_matches / 2.0, 1.0)  

        else:  # TEXT_ONLY  
            non_visual_count = len(question.split()) - sum(1 for keyword in self.visual_keywords   
                                                         if keyword in question_lower)  
            return min(non_visual_count / 10.0, 1.0)
