"""
validador de calidad para imágenes generadas
aquí implemento múltiples métricas de calidad y coherencia
"""

import logging
import numpy as np
from PIL import Image, ImageStat, ImageFilter
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import cv2

class ImageQualityValidator:
    """
    validador de calidad para imágenes técnicas generadas
    evalúo claridad, nitidez, composición y coherencia técnica
    """
    
    def __init__(self, min_quality_score: float = 0.6):
        self.logger = logging.getLogger(__name__)
        self.min_quality_score = min_quality_score
        
        # aquí defino los umbrales de calidad
        self.thresholds = {
            'sharpness_min': 100,
            'brightness_min': 50,
            'brightness_max': 200,
            'contrast_min': 30,
            'noise_max': 0.15,
            'color_balance_tolerance': 0.3
        }
        
        self.logger.info("imagequalityvalidator inicializado")
    
    def validate_image(self, image_path: str) -> Dict:
        """
        valido una imagen y retorno un reporte completo de calidad
        """
        try:
            image = Image.open(image_path)
            
            # ejecuto todas las validaciones
            scores = {
                'sharpness': self._check_sharpness(image),
                'brightness': self._check_brightness(image),
                'contrast': self._check_contrast(image),
                'noise': self._check_noise(image),
                'composition': self._check_composition(image),
                'color_balance': self._check_color_balance(image),
                'technical_clarity': self._check_technical_clarity(image)
            }
            
            # calculo score global
            global_score = self._calculate_global_score(scores)
            
            # determino si pasa validación
            passed = global_score >= self.min_quality_score
            
            # genero recomendaciones
            recommendations = self._generate_recommendations(scores)
            
            return {
                'passed': passed,
                'global_score': round(global_score, 3),
                'scores': {k: round(v, 3) for k, v in scores.items()},
                'recommendations': recommendations,
                'image_path': image_path,
                'size': image.size,
                'format': image.format,
                'mode': image.mode
            }
            
        except Exception as e:
            self.logger.error(f"error validando imagen: {e}")
            return {
                'passed': False,
                'error': str(e),
                'image_path': image_path
            }
    
    def _check_sharpness(self, image: Image.Image) -> float:
        """
        evalúo la nitidez usando laplacian, valores más altos indican mayor nitidez
        """
        gray = image.convert('L')
        img_array = np.array(gray)
        laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()
        score = min(laplacian_var / 500, 1.0)
        return score
    
    def _check_brightness(self, image: Image.Image) -> float:
        """
        evalúo el brillo y busco un rango equilibrado
        """
        gray = image.convert('L')
        stat = ImageStat.Stat(gray)
        brightness = stat.mean[0]
        
        if 80 <= brightness <= 170:
            score = 1.0
        elif brightness < 80:
            score = brightness / 80
        else:
            score = (255 - brightness) / (255 - 170)
        
        return max(0, score)
    
    def _check_contrast(self, image: Image.Image) -> float:
        """
        evalúo el contraste mediante desviación estándar
        """
        gray = image.convert('L')
        stat = ImageStat.Stat(gray)
        contrast = stat.stddev[0]
        score = min(contrast / 60, 1.0)
        return score
    
    def _check_noise(self, image: Image.Image) -> float:
        """
        detecto el ruido estimando la diferencia con un filtro mediano
        """
        gray = image.convert('L')
        img_array = np.array(gray)
        
        median_filtered = cv2.medianBlur(img_array, 5)
        noise = np.abs(img_array.astype(float) - median_filtered.astype(float))
        noise_level = noise.mean() / 255.0
        
        score = 1.0 - min(noise_level * 5, 1.0)
        return score
    
    def _check_composition(self, image: Image.Image) -> float:
        """
        evalúo composición básica dividiendo la imagen en cuadrantes
        """
        width, height = image.size
        img_array = np.array(image.convert('L'))
        
        h_mid, w_mid = height // 2, width // 2
        
        quadrants = [
            img_array[:h_mid, :w_mid],
            img_array[:h_mid, w_mid:],
            img_array[h_mid:, :w_mid],
            img_array[h_mid:, w_mid:]
        ]
        
        densities = [np.std(q) for q in quadrants]
        avg_density = np.mean(densities)
        balance = 1.0 - (np.std(densities) / (avg_density + 1e-6))
        
        return min(max(balance, 0), 1.0)
    
    def _check_color_balance(self, image: Image.Image) -> float:
        """
        evalúo el balance de color para evitar sesgos excesivos
        """
        if image.mode != 'RGB':
            return 1.0
        
        stat = ImageStat.Stat(image)
        r_mean, g_mean, b_mean = stat.mean[:3]
        deviation = np.std([r_mean, g_mean, b_mean])
        
        score = 1.0 - min(deviation / 100, 1.0)
        return score
    
    def _check_technical_clarity(self, image: Image.Image) -> float:
        """
        evalúo claridad técnica mediante detección de bordes
        """
        gray = image.convert('L')
        img_array = np.array(gray)
        
        edges = cv2.Canny(img_array, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        if 0.05 <= edge_density <= 0.20:
            score = 1.0
        elif edge_density < 0.05:
            score = edge_density / 0.05
        else:
            score = max(0, 1.0 - (edge_density - 0.20) / 0.30)
        
        return score
    
    def _calculate_global_score(self, scores: Dict[str, float]) -> float:
        """
        calculo el score global usando ponderaciones
        """
        weights = {
            'sharpness': 0.20,
            'technical_clarity': 0.20,
            'contrast': 0.15,
            'brightness': 0.15,
            'composition': 0.15,
            'noise': 0.10,
            'color_balance': 0.05
        }
        
        global_score = sum(scores[k] * weights[k] for k in scores)
        return global_score
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """
        genero recomendaciones basadas en los resultados
        """
        recommendations = []
        
        if scores['sharpness'] < 0.5:
            recommendations.append("imagen borrosa, recomiendo aumentar num_inference_steps a 75-100")
        
        if scores['brightness'] < 0.5:
            recommendations.append("imagen muy oscura o muy brillante, recomiendo agregar 'well-lit, clear' al prompt")
        
        if scores['contrast'] < 0.5:
            recommendations.append("contraste bajo, sugiero usar 'high contrast, clear lines'")
        
        if scores['noise'] < 0.6:
            recommendations.append("imagen ruidosa, mejora el negative prompt con 'clean, professional'")
        
        if scores['technical_clarity'] < 0.5:
            recommendations.append("poca claridad técnica, recomiendo 'technical diagram, clear lines'")
        
        if scores['composition'] < 0.5:
            recommendations.append("composición desbalanceada, prueba con 'centered, balanced layout'")
        
        if not recommendations:
            recommendations.append("imagen de buena calidad, sin recomendaciones")
        
        return recommendations
    
    def batch_validate(self, image_paths: List[str]) -> Dict:
        """
        valido múltiples imágenes y retorno un reporte agregado
        """
        results = []
        
        for path in image_paths:
            result = self.validate_image(path)
            results.append(result)
        
        passed_count = sum(1 for r in results if r.get('passed', False))
        avg_score = np.mean([r['global_score'] for r in results if 'global_score' in r])
        
        return {
            'total_images': len(image_paths),
            'passed': passed_count,
            'failed': len(image_paths) - passed_count,
            'pass_rate': passed_count / len(image_paths) if image_paths else 0,
            'average_score': round(avg_score, 3),
            'individual_results': results
        }
    
    def get_quality_summary(self, validation_result: Dict) -> str:
        """
        genero un resumen legible de la validación
        """
        if 'error' in validation_result:
            return f"error: {validation_result['error']}"
        
        passed = "aprobada" if validation_result['passed'] else "rechazada"
        score = validation_result['global_score']
        
        summary = f"""
{passed.upper()} - score global: {score:.2%}

scores detallados:
  nitidez: {validation_result['scores']['sharpness']:.2%}
  claridad técnica: {validation_result['scores']['technical_clarity']:.2%}
  contraste: {validation_result['scores']['contrast']:.2%}
  brillo: {validation_result['scores']['brightness']:.2%}
  composición: {validation_result['scores']['composition']:.2%}
  ruido: {validation_result['scores']['noise']:.2%}
  balance de color: {validation_result['scores']['color_balance']:.2%}

recomendaciones:
"""
        for rec in validation_result['recommendations']:
            summary += f"  • {rec}\n"
        
        return summary.strip()


# test del validador
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    validator = ImageQualityValidator(min_quality_score=0.6)
    
    print("validador de calidad de imágenes")
    print("="*50)
    print("\ncaracterísticas evaluadas:")
    print("  • nitidez")
    print("  • claridad técnica")
    print("  • contraste")
    print("  • brillo")
    print("  • composición")
    print("  • nivel de ruido")
    print("  • balance de colores")
    print("\nscore mínimo para aprobar: 60%")