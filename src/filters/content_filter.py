import logging
import re
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass

class FilterResult:
    allowed: bool
    reason:str=""
    blocked_terms: List[str]=None
    confidence: float = 1.0
    
class ContentFilter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.blocked_terms = {  
            'violence': {'kill', 'matar', 'murder', 'asesinato', 'weapon', 'arma', 'gun', 'pistola', 'violence', 'violencia', 'fight', 'pelea', 'attack', 'ataque'},  
            'adult_content': {'nude', 'desnudo', 'sexual', 'sexual', 'porn', 'pornografía', 'adult', 'adulto', 'explicit', 'explícito'},  
            'hate': {'hate', 'odio', 'racist', 'racista', 'nazi', 'nazi', 'terrorism', 'terrorismo', 'extremist', 'extremista'},  
            'illegal': {'drug', 'droga', 'illegal', 'ilegal', 'crime', 'crimen', 'steal', 'robar', 'hack', 'hackear', 'piracy', 'piratería'},  
            'self_harm': {'suicide', 'suicidio', 'self harm', 'autolesión', 'depression', 'depresión', 'cut', 'cortar', 'hurt myself', 'hacerme daño'},  
            'inappropriate': {'blood', 'sangre', 'gore', 'gore', 'death', 'muerte', 'torture', 'tortura', 'abuse', 'abuso'}

        }

        self.patterns = [  
            r'\b(how\s+to\s+(kill|hack|steal|make\s+(bomb|weapon)))\b',  
            r'\b(suicid|self\s+harm)\b',  
            r'\b(porn|nude|sexual)\b',  
        ]

        self.logger.info("ContentFilter inicializado")

    def validate_prompt(self, prompt: str) -> FilterResult:  
        """Valida un prompt contra contenido inapropiado"""  
        prompt_lower = prompt.lower()  
        blocked_found = []  
          
        for category, terms in self.blocked_terms.items():  
            for term in terms:  
                if term in prompt_lower:  
                    blocked_found.append(f"{category}:{term}")  
          
        for pattern in self.patterns:  
            if re.search(pattern, prompt_lower):  
                blocked_found.append(f"pattern:{pattern}")  
          
        if blocked_found:  
            return FilterResult(  
                allowed=False,  
                reason=f"Contenido bloqueado: {', '.join(blocked_found)}",  
                blocked_terms=blocked_found,  
                confidence=0.0  
            )  
          
        return FilterResult(allowed=True, confidence=1.0)  
  
    def sanitize_prompt(self, prompt: str) -> str:  
        """Limpia el prompt de caracteres problemáticos"""  
        prompt = re.sub(r'\s+', ' ', prompt.strip())  
        prompt = re.sub(r'[<>"\']', '', prompt)  
        return prompt[:500]


