import logging  
from typing import Dict, List, Optional, Tuple  
import re  
from difflib import SequenceMatcher  

class CoherenceValidator:  

    def __init__(self, min_coherence_score: float = 0.6):  
        self.logger = logging.getLogger(__name__)  
        self.min_coherence_score = min_coherence_score  

        self.technical_terms = {  
            'spring boot', 'mvc', 'controller', 'service', 'repository',  
            'rest api', 'microservices', 'architecture', 'diagram',  
            'component', 'layer', 'entity', 'dependency injection'  
        }  

        self.logger.info("CoherenceValidator inicializado")  

    def validate_cross_modal_coherence(self,   
                                     question: str,  
                                     text_answer: str,  
                                     image_prompt: str,  
                                     image_concept: str) -> Dict:  

        try:  
            question_terms = self._extract_technical_terms(question)  
            text_terms = self._extract_technical_terms(text_answer)  
            image_terms = self._extract_technical_terms(image_prompt)  
            concept_terms = self._extract_technical_terms(image_concept)  

            coherence_scores = {  
                'question_text_alignment': self._calculate_term_overlap(question_terms, text_terms),  
                'question_image_alignment': self._calculate_term_overlap(question_terms, image_terms),  
                'text_image_consistency': self._calculate_term_overlap(text_terms, image_terms),  
                'concept_relevance': self._calculate_term_overlap(question_terms, concept_terms),  
                'semantic_consistency': self._check_semantic_consistency(question, text_answer, image_concept)  
            }  

            global_score = self._calculate_global_coherence_score(coherence_scores)  

            passed = global_score >= self.min_coherence_score  

            recommendations = self._generate_coherence_recommendations(coherence_scores)  

            return {  
                'passed': passed,  
                'global_score': round(global_score, 3),  
                'scores': {k: round(v, 3) for k, v in coherence_scores.items()},  
                'recommendations': recommendations,  
                'term_analysis': {  
                    'question_terms': question_terms,  
                    'text_terms': text_terms,  
                    'image_terms': image_terms,  
                    'concept_terms': concept_terms  
                }  
            }  

        except Exception as e:  
            self.logger.error(f"Error validando coherencia cross-modal: {e}")  
            return {  
                'passed': False,  
                'error': str(e),  
                'global_score': 0.0  
            }  

    def _extract_technical_terms(self, text: str) -> List[str]:  
        text_lower = text.lower()  
        found_terms = []  

        for term in self.technical_terms:  
            if term in text_lower:  
                found_terms.append(term)  

        return found_terms  

    def _calculate_term_overlap(self, terms1: List[str], terms2: List[str]) -> float:  
        if not terms1 and not terms2:  
            return 1.0  
        if not terms1 or not terms2:  
            return 0.0  

        set1, set2 = set(terms1), set(terms2)  
        intersection = set1.intersection(set2)  
        union = set1.union(set2)  

        return len(intersection) / len(union) if union else 0.0  

    def _check_semantic_consistency(self, question: str, text_answer: str, image_concept: str) -> float:  
        question_concept_sim = SequenceMatcher(None, question.lower(), image_concept.lower()).ratio()  
        text_concept_sim = SequenceMatcher(None, text_answer.lower(), image_concept.lower()).ratio()  

        return (question_concept_sim + text_concept_sim) / 2  

    def _calculate_global_coherence_score(self, scores: Dict[str, float]) -> float:  
        weights = {  
            'question_text_alignment': 0.25,  
            'question_image_alignment': 0.20,  
            'text_image_consistency': 0.25,  
            'concept_relevance': 0.20,  
            'semantic_consistency': 0.10  
        }  

        return sum(scores[k] * weights[k] for k in scores)  

    def _generate_coherence_recommendations(self, scores: Dict[str, float]) -> List[str]:  
        recommendations = []  

        if scores['question_text_alignment'] < 0.5:  
            recommendations.append("La respuesta de texto no alinea bien con la pregunta, considera reformular")  

        if scores['question_image_alignment'] < 0.5:  
            recommendations.append("La imagen generada no refleja bien la pregunta, ajusta el prompt")  

        if scores['text_image_consistency'] < 0.5:  
            recommendations.append("Hay inconsistencia entre texto e imagen, revisa la coherencia")  

        if scores['concept_relevance'] < 0.5:  
            recommendations.append("El concepto de imagen no es relevante para la pregunta")  

        if scores['semantic_consistency'] < 0.6:  
            recommendations.append("La consistencia semántica es baja, revisa la relación entre componentes")  

        if not recommendations:  
            recommendations.append("Buena coherencia cross-modal entre texto e imagen")  

        return recommendations  

    def batch_validate_coherence(self, results: List[Dict]) -> Dict:  
        validation_results = []  

        for result in results:  
            if result.get('image_generated'):  
                validation = self.validate_cross_modal_coherence(  
                    result.get('question', ''),  
                    result.get('text_answer', ''),  
                    result.get('image_prompt', ''),  
                    result.get('image_concept', '')  
                )  
                validation_results.append(validation)  

        if not validation_results:  
            return {'error': 'No hay resultados cross-modal para validar'}  

        passed_count = sum(1 for r in validation_results if r.get('passed', False))  
        avg_score = sum(r['global_score'] for r in validation_results) / len(validation_results)  

        return {  
            'total_validated': len(validation_results),  
            'passed': passed_count,  
            'failed': len(validation_results) - passed_count,  
            'pass_rate': passed_count / len(validation_results),  
            'average_score': round(avg_score, 3),  
            'individual_results': validation_results  
        }
