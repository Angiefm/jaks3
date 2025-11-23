import logging
import requests
import base64
from typing import Dict, Optional, List
from pathlib import Path
import time
from io import BytesIO
from PIL import Image

class ImageGenerator:

    def __init__(self, api_key: str, output_dir: str = "data/generated_images"):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        self.style_templates = {
            "diagram": "technical diagram, clean lines, professional, white background, UML style",
            "architecture": "system architecture diagram, boxes and arrows, clean design, technical illustration",
            "flowchart": "flowchart diagram, sequential steps, clear connections, professional style",
            "class_diagram": "UML class diagram, object-oriented design, structured layout, professional",
            "infographic": "technical infographic, modern design, clear typography, professional colors"
        }
        self.logger.info("ImageGenerator (Stability AI) inicializado correctamente")
    def text_to_prompt(self, technical_query: str, style: str = "diagram") -> str:
        technical_keywords = self._extract_technical_keywords(technical_query)
        style_suffix = self.style_templates.get(style, self.style_templates["diagram"])
        prompt = f"{technical_query}, {style_suffix}, high quality, detailed, professional rendering"

        if technical_keywords:
            keywords_str = ", ".join(technical_keywords)
            prompt = f"{prompt}, featuring {keywords_str}"

        prompt = self._clean_prompt(prompt)
        self.logger.info(f"Prompt generado: {prompt[:100]}...")
        return prompt
    def _extract_technical_keywords(self, query: str) -> List[str]:
        tech_terms = {
            "spring boot", "spring mvc", "rest api", "microservices",
            "controller", "service", "repository", "entity",
            "dependency injection", "annotation", "configuration",
            "hibernate", "jpa", "database", "authentication",
            "authorization", "security", "mvc pattern", "layers",
            "architecture", "design pattern", "class diagram",
            "sequence diagram", "component diagram"
        }
        query_lower = query.lower()
        found_keywords = []
        for term in tech_terms:
            if term in query_lower:
                found_keywords.append(term)
        return found_keywords[:3]

    def _clean_prompt(self, prompt: str) -> str:
        """Limpia y optimiza el prompt"""
        prompt = prompt.replace("\n", " ").replace("\t", " ")
        prompt = " ".join(prompt.split())
        if len(prompt) > 300:
            prompt = prompt[:300]
        return prompt
    def generate_image(self, 
                      prompt: str, 
                      negative_prompt: Optional[str] = None,
                      save_path: Optional[str] = None) -> Dict:
        if negative_prompt is None:
            negative_prompt = "blurry, low quality, distorted, ugly, bad anatomy, text watermark"
        self.logger.info(f"Generando imagen con prompt: {prompt[:50]}...")
        try:
            payload = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    },
                    {
                        "text": negative_prompt,
                        "weight": -1
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }  
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120
            )    
            if response.status_code != 200:
                error_msg = f"API error ({response.status_code}): {response.text}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "prompt": prompt
                }
            
            data = response.json()
            
            if not data.get("artifacts"):
                return {
                    "success": False,
                    "error": "no se generó ninguna imagen",
                    "prompt": prompt
                }
            
            image_data = data["artifacts"][0]
            image_base64 = image_data.get("base64")
            
            if not image_base64:
                return {
                    "success": False,
                    "error": "no se encontró imagen en la respuesta",
                    "prompt": prompt
                }
            
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))
            
            if save_path is None:
                timestamp = int(time.time())
                filename = f"generated_{timestamp}.png"
                save_path = self.output_dir / filename
            else:
                save_path = Path(save_path)
            
            image.save(save_path)
            self.logger.info(f"imagen guardada en: {save_path}")
            
            return {
                "success": True,
                "path": str(save_path),
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "size": image.size,
                "format": image.format
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"error en request a API: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }
        except Exception as e:
            self.logger.error(f"Error generando imagen: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }
    def generate_from_query(self, 
                          technical_query: str,
                          style: str = "diagram",
                          **kwargs) -> Dict:
        prompt = self.text_to_prompt(technical_query, style)
        result = self.generate_image(prompt, **kwargs)
        result["original_query"] = technical_query
        result["style"] = style
        return result
    def batch_generate(self, queries: List[str], style: str = "diagram") -> List[Dict]:
        results = []
        
        for i, query in enumerate(queries):
            self.logger.info(f"Generando imagen {i+1}/{len(queries)}")
            result = self.generate_from_query(query, style)
            results.append(result)
            
            if i < len(queries) - 1:
                time.sleep(3)
        
        return results
    
    def list_available_styles(self) -> List[str]:
        return list(self.style_templates.keys())

    def get_style_description(self, style: str) -> str:
        return self.style_templates.get(style, "Style not found")
