import logging
from typing import Dict, List, Optional
from pathlib import Path
import time

# importo componentes
import sys
sys.path.append(str(Path(__file__).parent))

from image_generator import ImageGenerator
from image_quality_validator import ImageQualityValidator
from style_controller import StyleController, StyleConfig, DiagramType, ColorScheme

class AdvancedImageGenerator:
    """
    generador avanzado con control de calidad y estilos
    """
    
    def __init__(self, 
                 api_key: str,
                 min_quality_score: float = 0.6,
                 max_retries: int = 3,
                 output_dir: str = "data/generated_images"):
        
        self.logger = logging.getLogger(__name__)
        
        # inicializo componentes
        self.generator = ImageGenerator(api_key, output_dir)
        self.validator = ImageQualityValidator(min_quality_score)
        self.style_controller = StyleController()
        
        self.max_retries = max_retries
        self.output_dir = Path(output_dir)
        
        self.logger.info("advancedimagegenerator inicializado")
    
    def generate_with_quality_check(self,
                                   technical_concept: str,
                                   style_config: Optional[StyleConfig] = None,
                                   auto_retry: bool = True) -> Dict:
        """
        genero una imagen con validacion automatica de calidad
        si la calidad no alcanza el minimo, reintento
        """
        # si no hay config, sugiero una
        if style_config is None:
            style_config = self.style_controller.suggest_style_for_concept(technical_concept)
            self.logger.info(f"estilo auto-sugerido: {style_config.diagram_type.value}")
        
        # construyo prompts optimizados
        prompt = self.style_controller.build_prompt(technical_concept, style_config)
        negative_prompt = self.style_controller.build_negative_prompt(style_config)
        
        attempts = 0
        best_result = None
        best_score = 0
        
        while attempts < self.max_retries:
            attempts += 1
            self.logger.info(f"intento {attempts}/{self.max_retries}")
            
            # genero imagen
            # Genero imagen (sin parámetros no soportados)
            gen_result = self.generator.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt
            )
            
            if not gen_result['success']:
                self.logger.error(f"error generando: {gen_result.get('error')}")
                continue
            
            # valido calidad
            validation = self.validator.validate_image(gen_result['path'])
            
            self.logger.info(
                f"calidad: {validation['global_score']:.2%} "
                f"({'aprobada' if validation['passed'] else 'rechazada'})"
            )
            
            # guardo mejor resultado
            if validation['global_score'] > best_score:
                best_score = validation['global_score']
                best_result = {
                    'generation': gen_result,
                    'validation': validation,
                    'attempt': attempts,
                    'style_config': style_config
                }
            
            # si paso validacion, termino
            if validation['passed']:
                best_result['success'] = True
                break
            
            # si no puedo reintentar, paro
            if not auto_retry:
                break
            
            # espero antes de reintentar
            if attempts < self.max_retries:
                self.logger.info("reintentando con parametros mejorados...")
                time.sleep(2)
        
        # si no hubo exito pero tengo resultado
        if best_result and 'success' not in best_result:
            best_result['success'] = False
            best_result['reason'] = 'no alcanzo la calidad minima despues de reintentos'
        
        return best_result or {
            'success': False,
            'error': 'no se pudo generar ninguna imagen'
        }
    
    def generate_variations(self,
                          technical_concept: str,
                          num_variations: int = 3) -> List[Dict]:
        """
        genero multiples variaciones cambiando estilos
        """
        # obtengo estilo base
        base_style = self.style_controller.suggest_style_for_concept(technical_concept)
        
        # genero variaciones
        style_variations = self.style_controller.get_style_variations(base_style)
        styles_to_try = [base_style] + style_variations[:num_variations-1]
        
        results = []
        
        for i, style in enumerate(styles_to_try[:num_variations]):
            self.logger.info(f"\ngenerando variacion {i+1}/{num_variations}")
            self.logger.info(f"estilo: {style.diagram_type.value}, {style.color_scheme.value}")
            
            result = self.generate_with_quality_check(
                technical_concept,
                style_config=style,
                auto_retry=False
            )
            
            results.append(result)
            
            if i < len(styles_to_try) - 1:
                time.sleep(3)
        
        return results
    
    def generate_with_preset(self,
                           technical_concept: str,
                           preset_name: str = 'documentation') -> Dict:
        """
        genero usando un preset predefinido
        """
        preset_config = self.style_controller.get_preset(preset_name)
        
        if not preset_config:
            self.logger.error(f"preset '{preset_name}' no encontrado")
            available = self.style_controller.list_presets()
            return {
                'success': False,
                'error': f"preset invalido. disponibles: {available}"
            }
        
        return self.generate_with_quality_check(technical_concept, preset_config)
    
    def batch_generate_concepts(self,
                               concepts: List[str],
                               style: str = 'auto') -> Dict:
        """
        genero multiples conceptos con validacion agregada
        """
        results = []
        successful = 0
        failed = 0
        
        for i, concept in enumerate(concepts):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"concepto {i+1}/{len(concepts)}: {concept}")
            self.logger.info('='*60)
            
            if style == 'auto':
                result = self.generate_with_quality_check(concept)
            else:
                result = self.generate_with_preset(concept, style)
            
            results.append({
                'concept': concept,
                'result': result
            })
            
            if result.get('success'):
                successful += 1
            else:
                failed += 1
            
            if i < len(concepts) - 1:
                time.sleep(3)
        
        return {
            'total': len(concepts),
            'successful': successful,
            'failed': failed,
            'success_rate': successful / len(concepts) if concepts else 0,
            'results': results
        }
    
    def get_generation_report(self, result: Dict) -> str:
        """
        genero un reporte en formato legible
        """
        if not result.get('success'):
            return f"generacion fallida: {result.get('error', 'unknown error')}"
        
        gen = result['generation']
        val = result['validation']
        style = result.get('style_config')
        
        report = f"""
generacion exitosa

archivo: {gen['path']}
estilo: {style.diagram_type.value if style else 'auto'} - {style.color_scheme.value if style else 'n/a'}
intentos: {result['attempt']}

calidad
  score global: {val['global_score']:.2%}
  estado: {'aprobada' if val['passed'] else 'aceptable'}

  metricas:
    nitidez: {val['scores']['sharpness']:.2%}
    claridad tecnica: {val['scores']['technical_clarity']:.2%}
    contraste: {val['scores']['contrast']:.2%}
    brillo: {val['scores']['brightness']:.2%}
    composicion: {val['scores']['composition']:.2%}

recomendaciones:
"""
        for rec in val['recommendations']:
            report += f"  - {rec}\n"
        
        return report.strip()
