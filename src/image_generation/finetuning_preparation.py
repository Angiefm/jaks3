import logging
import json
from pathlib import Path
from typing import List, Dict, Tuple
import shutil
from pil import Image
import requests
from io import BytesIO

class finetuningpreparation:
 
    def __init__(self, output_dir: str = "data/finetuning"):
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        
        # creo estructura de directorios
        self.images_dir = self.output_dir / "images"
        self.captions_dir = self.output_dir / "captions"
        self.metadata_file = self.output_dir / "metadata.jsonl"
        
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.captions_dir.mkdir(parents=True, exist_ok=True)
        
        # defino templates
        self.caption_templates = {
            'architecture': [
                "technical architecture diagram showing {concept}",
                "system architecture with {concept}",
                "architectural blueprint of {concept}",
                "layered architecture diagram for {concept}"
            ],
            'uml': [
                "uml class diagram depicting {concept}",
                "object-oriented design for {concept}",
                "class structure showing {concept}",
                "uml diagram representing {concept}"
            ],
            'flowchart': [
                "flowchart illustrating {concept}",
                "process flow diagram for {concept}",
                "algorithmic flowchart of {concept}",
                "step-by-step flow showing {concept}"
            ],
            'sequence': [
                "sequence diagram showing {concept}",
                "interaction diagram for {concept}",
                "message flow in {concept}",
                "temporal sequence of {concept}"
            ]
        }
        
        self.logger.info("inicializo finetuningpreparation")
    
    def create_training_sample(self,
                              image_path: str,
                              caption: str,
                              category: str = "general",
                              metadata: Dict = None) -> bool:
        """
        creo una muestra de entrenamiento (imagen + caption)
        """
        try:
            image = Image.open(image_path)
            
            if image.size != (512, 512):
                image = image.resize((512, 512), Image.Resampling.LANCZOS)
            
            sample_id = len(list(self.images_dir.glob("*.png")))
            image_filename = f"sample_{sample_id:04d}.png"
            caption_filename = f"sample_{sample_id:04d}.txt"
            
            image.save(self.images_dir / image_filename)
            
            with open(self.captions_dir / caption_filename, 'w') as f:
                f.write(caption)
            
            metadata_entry = {
                'image': image_filename,
                'caption': caption,
                'category': category,
                'metadata': metadata or {}
            }
            
            with open(self.metadata_file, 'a') as f:
                f.write(json.dumps(metadata_entry) + '\n')
            
            self.logger.info(f"creo muestra: {image_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"error creando muestra: {e}")
            return False
    
    def generate_caption_variations(self, 
                                   base_concept: str,
                                   category: str = 'architecture',
                                   num_variations: int = 3) -> List[str]:
        """
        genero variaciones de captions para un concepto
        """
        templates = self.caption_templates.get(category, self.caption_templates['architecture'])
        
        captions = []
        for i in range(min(num_variations, len(templates))):
            caption = templates[i].format(concept=base_concept)
            
            variations = [
                caption,
                f"{caption}, professional style",
                f"{caption}, clean and clear",
                f"technical illustration: {caption}"
            ]
            captions.extend(variations[:num_variations])
        
        return captions[:num_variations]
    
    def download_reference_images(self, 
                                  search_terms: List[str],
                                  max_per_term: int = 5) -> int:
        """
        descargo imagenes de referencia de fuentes publicas
        """
        downloaded = 0
        
        reference_urls = {
            'spring_architecture': [
                'https://raw.githubusercontent.com/spring-guides/gs-rest-service/main/complete/src/main/resources/static/images/architecture.png'
            ]
        }
        
        self.logger.warning("descarga de referencias solo para uso educativo")
        
        for term, urls in reference_urls.items():
            for i, url in enumerate(urls[:max_per_term]):
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        
                        ref_path = self.images_dir / f"reference_{term}_{i}.png"
                        image.save(ref_path)
                        
                        caption = f"technical diagram showing {term.replace('_', ' ')}"
                        self.create_training_sample(
                            str(ref_path),
                            caption,
                            category=term
                        )
                        
                        downloaded += 1
                        self.logger.info(f"descargo referencia: {term}_{i}")
                        
                except Exception as e:
                    self.logger.warning(f"no pude descargar {url}: {e}")
        
        return downloaded
    
    def create_synthetic_dataset(self, num_samples: int = 20) -> Dict:
        """
        creo dataset sintetico de conceptos java/spring
        """
        concepts = [
            ("spring boot layered architecture", "architecture"),
            ("mvc pattern in spring", "architecture"),
            ("microservices architecture", "architecture"),
            ("rest api structure", "architecture"),
            ("spring bean lifecycle", "uml"),
            ("controller-service-repository pattern", "uml"),
            ("dependency injection", "uml"),
            ("jpa entity relationships", "uml"),
            ("spring security filter chain", "flowchart"),
            ("request processing in spring mvc", "flowchart"),
            ("transaction management flow", "flowchart"),
            ("authentication flow", "sequence"),
            ("spring boot starter dependencies", "architecture"),
            ("spring cloud components", "architecture"),
            ("hibernate architecture", "architecture")
        ]
        
        created = {
            'total': 0,
            'by_category': {}
        }
        
        for concept, category in concepts[:num_samples]:
            captions = self.generate_caption_variations(concept, category, 2)
            
            for caption in captions:
                created['total'] += 1
                created['by_category'][category] = created['by_category'].get(category, 0) + 1
                
                self.logger.info(f"creo caption: {caption}")
        
        return created
    
    def prepare_dreambooth_format(self, class_name: str = "technical_diagram"):
        """
        preparo dataset en formato dreambooth
        """
        dreambooth_dir = self.output_dir / "dreambooth_format"
        instance_dir = dreambooth_dir / "instance_images"
        class_dir = dreambooth_dir / "class_images"
        
        instance_dir.mkdir(parents=True, exist_ok=True)
        class_dir.mkdir(parents=True, exist_ok=True)
        
        for img in self.images_dir.glob("*.png"):
            if not img.name.startswith("reference_"):
                shutil.copy(img, instance_dir / img.name)
        
        self.logger.info(f"preparo dataset dreambooth en {dreambooth_dir}")
        
        return {
            'instance_dir': str(instance_dir),
            'class_dir': str(class_dir),
            'class_name': class_name,
            'num_images': len(list(instance_dir.glob("*.png")))
        }
    
    def prepare_lora_format(self):
        """
        preparo dataset en formato lora training
        """
        lora_dir = self.output_dir / "lora_format"
        lora_dir.mkdir(parents=True, exist_ok=True)
        
        for img in self.images_dir.glob("*.png"):
            caption_file = self.captions_dir / f"{img.stem}.txt"
            
            if caption_file.exists():
                shutil.copy(img, lora_dir / img.name)
                shutil.copy(caption_file, lora_dir / f"{img.stem}.txt")
        
        self.logger.info(f"preparo dataset lora en {lora_dir}")
        
        return {
            'output_dir': str(lora_dir),
            'num_pairs': len(list(lora_dir.glob("*.png")))
        }
    
    def get_dataset_statistics(self) -> Dict:
        """
        obtengo estadisticas del dataset
        """
        num_images = len(list(self.images_dir.glob("*.png")))
        num_captions = len(list(self.captions_dir.glob("*.txt")))
        
        categories = {}
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    cat = entry.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_images': num_images,
            'total_captions': num_captions,
            'categories': categories,
            'output_dir': str(self.output_dir),
            'ready_for_training': num_images >= 10 and num_images == num_captions
        }
    
    def generate_training_config(self, 
                                training_type: str = "lora") -> Dict:
        """
        genero configuracion de entrenamiento
        """
        if training_type == "lora":
            config = {
                'training_type': 'lora',
                'base_model': 'stabilityai/stable-diffusion-2-1',
                'dataset_path': str(self.output_dir / 'lora_format'),
                'output_path': 'models/lora_java_spring',
                'hyperparameters': {
                    'learning_rate': 1e-4,
                    'train_batch_size': 1,
                    'max_train_steps': 1000,
                    'lora_rank': 4,
                    'gradient_accumulation_steps': 4
                },
                'recommended_steps': 'minimo 500 steps, idealmente 1000-2000'
            }
        else:
            config = {
                'training_type': 'dreambooth',
                'base_model': 'stabilityai/stable-diffusion-2-1',
                'dataset_path': str(self.output_dir / 'dreambooth_format'),
                'output_path': 'models/dreambooth_java_spring',
                'hyperparameters': {
                    'learning_rate': 2e-6,
                    'train_batch_size': 1,
                    'max_train_steps': 800,
                    'gradient_accumulation_steps': 1
                },
                'recommended_steps': 'minimo 400 steps, idealmente 800-1200'
            }
        
        config_file = self.output_dir / f"{training_type}_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info(f"genero configuracion: {config_file}")
        return config


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    prep = finetuningpreparation()
    
    print("sistema de preparacion de fine-tuning")
    print("="*50)
    
    print("\ngenero dataset sintetico...")
    result = prep.create_synthetic_dataset(num_samples=10)
    print(f"creo: {result['total']} samples")
    print(f"por categoria: {result['by_category']}")
    
    print("\nestadisticas del dataset:")
    stats = prep.get_dataset_statistics()
    print(f"  imagenes: {stats['total_images']}")
    print(f"  captions: {stats['total_captions']}")
    print(f"  listo para training: {stats['ready_for_training']}")
    
    print("\ngenero configuraciones de entrenamiento...")
    lora_config = prep.generate_training_config("lora")
    print(f"  lora config: {lora_config['hyperparameters']}")
