import logging
import requests
from typing import Dict, Optional, List
from pathlib import Path
import time
from io import BytesIO
from PIL import Image

class ImageGenerator:
    """Generador de imágenes técnicas usando Stability AI directamente"""

    def __init__(self, api_key: str, output_dir: str = "data/generated_images"):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Endpoint de Stability AI (funciona en cualquier país)
        self.api_url = "https://api.stability.ai/v2beta/stable-image/generate/core"

        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }

        self.style_templates = {
            "diagram": "technical diagram, clean lines, professional, white background, UML style",
            "architecture": "system architecture diagram, boxes and arrows, clean design, technical illustration",
            "flowchart": "flowchart diagram, sequential steps, clear connections, professional style",
            "class_diagram": "UML class diagram, object-oriented design, structured layout, professional",
            "infographic": "technical infographic, modern design, clear typography, professional colors"
        }

        self.logger.info("ImageGenerator (Stability) inicializado correctamente")

    def text_to_prompt(self, technical_query: str, style: str = "diagram") -> str:
        keywords = self._extract_technical_keywords(technical_query)
        style_suffix = self.style_templates.get(style, self.style_templates["diagram"])

        prompt = f"{technical_query}, {style_suffix}, high quality, detailed, professional rendering"

        if keywords:
            prompt = f"{prompt}, featuring {', '.join(keywords)}"

        return self._clean_prompt(prompt)

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
        return [t for t in tech_terms if t in query_lower][:3]

    def _clean_prompt(self, prompt: str) -> str:
        prompt = " ".join(prompt.split())
        return prompt[:300]

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        save_path: Optional[str] = None
    ) -> Dict:

        if negative_prompt is None:
            negative_prompt = "blurry, low quality, distorted, watermark, text"

        self.logger.info(f"Generando imagen con prompt: {prompt[:50]}...")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "image/*"                  # <- CLAVE!
            }
        
            # La API requiere 'prompt' y 'negative_prompt' como campos en multipart/form-data
            form_data = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "aspect_ratio": "1:1",
                "mode": "text-to-image"
            }
        
            response = requests.post(
                self.api_url,
                headers=headers,
                files={key: (None, value) for key, value in form_data.items()},
                timeout=60
            )
        
            if response.status_code != 200:
                raise Exception(f"API error: {response.text}")
        
            # Guardar imagen
            image_bytes = response.content
            image = Image.open(BytesIO(image_bytes))
        
            if save_path is None:
                filename = f"generated_{int(time.time())}.png"
                save_path = self.output_dir / filename
            else:
                save_path = Path(save_path)
        
            image.save(save_path)
        
            return {
                "success": True,
                "path": str(save_path),
                "prompt": prompt,
                "size": image.size
            }
        
        except Exception as e:
            self.logger.error(f"Error generando imagen: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }

    def generate_from_query(self, technical_query: str, style: str = "diagram", **kwargs):
        prompt = self.text_to_prompt(technical_query, style)
        result = self.generate_image(prompt, **kwargs)
        result["original_query"] = technical_query
        result["style"] = style
        return result

    def list_available_styles(self) -> List[str]:
        return list(self.style_templates.keys())

    def get_style_description(self, style: str) -> str:
        return self.style_templates.get(style, "Style not found")
