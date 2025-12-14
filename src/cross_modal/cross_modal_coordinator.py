import logging  
from typing import Dict, Optional  
from .modality_selector import ModalitySelector, ModalityType  
from .coherence_validator import CoherenceValidator
from src.filters.content_filter import ContentFilter  


class CrossModalCoordinator:  

    def __init__(self, rag_engine, image_generator):  
        self.rag_engine = rag_engine  
        self.image_generator = image_generator  
        self.coherence_validator = CoherenceValidator(min_coherence_score=0.6)  
        self.modality_selector = ModalitySelector()  
        self.logger = logging.getLogger(__name__)  
        self.content_filter = ContentFilter()

    def _should_generate_image(self, question: str, answer: str) -> bool:  
        diagram_keywords = [  
            'arquitectura', 'diagrama', 'flujo', 'estructura',  
            'componentes', 'capas', 'mvc', 'rest', 'api'  
        ]  

        question_lower = question.lower()  
        answer_lower = answer.lower()  

        return any(keyword in question_lower or keyword in answer_lower  
                   for keyword in diagram_keywords)  

    def process_cross_modal_query(self, question: str, top_k: int = 3) -> Dict:  
        try:  
            filter_result = self.content_filter.validate_prompt(question)  
            if not filter_result.allowed:  
                self.logger.warning(f"Query bloqueada: {filter_result.reason}")  
                return {  
                    'text_answer': "no puedo procesar esta solicitud debido a contenido inapropiado",  
                    'sources': [],  
                    'image_generated': False,  
                    'modality': 'text_only',  
                    'confidence': 0.0,  
                    'filter_blocked': True,  
                    'filter_reason': filter_result.reason  
                }  
              
            clean_question = self.content_filter.sanitize_prompt(question)  
              
            chat_result = self.rag_engine.generate_answer(clean_question, top_k)  
              
            modality = self.modality_selector.select_modality(  
                question, 
                chat_result.get('sources', [])  
            )  
              
            if modality == ModalityType.TEXT_AND_IMAGE:  
                image_result = self.image_generator.generate_with_quality_check(clean_question)  
                  
                coherence_validation = None  
                coherence_passed = False  
                  
                if image_result.get('success'):  
                    coherence_validation = self.coherence_validator.validate_cross_modal_coherence(  
                        question=question, 
                        text_answer=chat_result['answer'],  
                        image_prompt=image_result.get('prompt', ''),  
                        image_concept=clean_question 
                    )  
                    coherence_passed = coherence_validation['passed']  
                  
                return {  
                    'text_answer': chat_result['answer'],  
                    'sources': chat_result['sources'],  
                    'image_generated': True,  
                    'image_path': image_result.get('path'),  
                    'modality': 'text_and_image',  
                    'confidence': self.modality_selector.get_modality_confidence(question, modality),  
                    'coherence_validation': coherence_validation,  
                    'coherence_passed': coherence_passed  
                }  
              
            elif modality == ModalityType.IMAGE_ONLY:  
                image_result = self.image_generator.generate_with_quality_check(clean_question)  
                return {  
                    'text_answer': None,  
                    'sources': [],  
                    'image_generated': True,  
                    'image_path': image_result.get('path'),  
                    'modality': 'image_only',  
                    'confidence': self.modality_selector.get_modality_confidence(question, modality)  
                }  
              
            else:  # TEXT_ONLY  
                return {  
                    'text_answer': chat_result['answer'],  
                    'sources': chat_result['sources'],  
                    'image_generated': False,  
                    'modality': 'text_only',  
                    'confidence': self.modality_selector.get_modality_confidence(question, modality)  
                }  
          
        except Exception as e:  
            self.logger.error(f"Error en procesamiento cross-modal: {e}", exc_info=True)  
            return {  
                'text_answer': f"Error en el procesamiento cross-modal: {str(e)}",  
                'sources': [],  
                'image_generated': False,  
                'modality': 'text_only',  
                'confidence': 0.0  
            }
