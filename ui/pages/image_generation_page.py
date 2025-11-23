"""
página de streamlit para generación de imágenes técnicas
tarea 5: demostración de mitad de curso
"""

import streamlit as st
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from PIL import Image
import time

# configuración de paths
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.image_generation.advanced_image_generator import AdvancedImageGenerator
from src.image_generation.style_controller import StyleController, DiagramType, ColorScheme

load_dotenv()

# configuración de la página
st.set_page_config(
    page_title="Generador de Diagramas Técnicos",
    page_icon="🎨",
    layout="wide"
)

# css personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #7c3aed;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(124, 58, 237, 0.2);
        font-weight: bold;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #a7f3d0, #6ee7b7);
        color: #064e3b;
        border-radius: 12px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-size: 1rem;
        font-weight: bold;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #6ee7b7, #34d399);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(167, 243, 208, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid #fcd34d;
        margin: 0.5rem 0;
    }
    
    .quality-score {
        font-size: 2rem;
        font-weight: bold;
        color: #7c3aed;
    }
</style>
""", unsafe_allow_html=True)

# inicialización del estado
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []

def initialize_generator():
    """inicializo el generador con cache"""
    api_key = os.getenv("STABILITY_API_KEY")
    
    if not api_key:
        st.error("❌ No se encontró STABILITY_API_KEY en .env")
        st.info("""
        para usar el generador:
        1. crea cuenta en https://huggingface.co
        2. obtén token en settings > access tokens
        3. agrégalo a .env: HUGGINGFACE_API_KEY=hf_...
        """)
        return None
    
    return AdvancedImageGenerator(
        api_key=api_key,
        min_quality_score=0.6,
        max_retries=2
    )

def show_quality_metrics(validation_result):
    """muestro métricas de calidad de forma visual"""
    scores = validation_result['scores']
    
    st.markdown("### 📊 Métricas de Calidad")
    
    global_score = validation_result['global_score']
    status = "APROBADA" if validation_result['passed'] else "MEJORABLE"
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="text-align: center;">
                <div class="quality-score">{global_score:.0%}</div>
                <div style="font-size: 1.2rem;">{status}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="text-align: center;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #7c3aed;">
                    intento {validation_result.get('attempt', 1)}
                </div>
                <div style="font-size: 1rem;">de {validation_result.get('max_attempts', 3)} máximo</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("#### scores detallados")
    
    metrics_data = {
        'nitidez': scores['sharpness'],
        'claridad técnica': scores['technical_clarity'],
        'contraste': scores['contrast'],
        'brillo': scores['brightness'],
        'composición': scores['composition'],
        'ruido': scores['noise'],
        'balance color': scores['color_balance']
    }
    
    for metric_name, score in metrics_data.items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(metric_name)
        with col2:
            st.progress(score)
            st.caption(f"{score:.0%}")

def main():
    st.markdown('<h1 class="main-header">🎨 Generador de Diagramas Técnicos</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-bottom: 2rem;">
        sistema inteligente de generación de imágenes para conceptos java/spring boot
        <br>con validación automática de calidad y control de estilos
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        preset_options = {
            'Auto-detectar': None,
            'Tutorial (Simple)': 'tutorial',
            'Presentación (Vibrante)': 'presentation',
            'Documentación (Detallado)': 'documentation',
            'Spring Official': 'spring_official'
        }
        
        selected_preset = st.selectbox(
            "Estilo de Diagrama",
            options=list(preset_options.keys())
        )
        
        st.markdown("---")
        st.subheader("control de calidad")
        
        min_quality = st.slider(
            "score mínimo de calidad",
            min_value=0.3,
            max_value=0.9,
            value=0.6,
            step=0.05,
            format="%.0f%%"
        )
        
        max_retries = st.slider(
            "reintentos máximos",
            min_value=1,
            max_value=5,
            value=2
        )
        
        st.markdown("---")
        st.subheader("sistema")
        st.info("""
        modelo: stable diffusion 2.1
        
        características:
        - 8 tipos de diagramas
        - 6 esquemas de color
        - validación con 7 métricas
        - reintentos inteligentes
        """)

    tab1, tab2, tab3 = st.tabs(["🎨 Generar", "🖼️ Galería", "📊 Estadísticas"])
    
    with tab1:
        show_generation_tab(preset_options[selected_preset], min_quality, max_retries)
    
    with tab2:
        show_gallery_tab()
    
    with tab3:
        show_statistics_tab()

def show_generation_tab(preset, min_quality, max_retries):
    """tab de generación de imágenes"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("describe tu diagrama")
        
        examples = [
            "Spring Boot REST API with controller, service, repository layers",
            "Spring Security authentication flow with JWT",
            "Microservices architecture with service discovery",
            "JPA entity relationships with one-to-many mappings",
            "Spring MVC request processing lifecycle"
        ]
        
        example_selected = st.selectbox(
            "ejemplos rápidos:",
            options=[""] + examples
        )
        
        concept = st.text_area(
            "concepto técnico:",
            value=example_selected if example_selected else "",
            height=100
        )
    
    with col2:
        st.subheader("vista previa de estilo")
        
        if concept:
            controller = StyleController()
            suggested_style = controller.suggest_style_for_concept(concept)
            
            st.info(f"""
            tipo: {suggested_style.diagram_type.value}
            colores: {suggested_style.color_scheme.value}
            complejidad: {suggested_style.complexity}
            """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "🎨 Generar Diagrama",
            disabled=not concept,
            use_container_width=True
        )
    
    if generate_button and concept:
        generate_image(concept, preset, min_quality, max_retries)

def generate_image(concept, preset, min_quality, max_retries):
    """genero imagen con validación"""
    
    generator = initialize_generator()
    if not generator:
        return
    
    generator.min_quality_score = min_quality
    generator.max_retries = max_retries
    
    progress_container = st.container()
    
    with progress_container:
        st.markdown("---")
        st.subheader("generando diagrama...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("inicializando generador...")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        status_text.text("generando imagen...")
        progress_bar.progress(30)
        
        start_time = time.time()
        
        try:
            if preset:
                result = generator.generate_with_preset(concept, preset)
            else:
                result = generator.generate_with_quality_check(concept)
            
            elapsed_time = time.time() - start_time
            
            progress_bar.progress(70)
            
            if result.get('success'):
                status_text.text("validando calidad...")
                progress_bar.progress(90)
                time.sleep(0.5)
                
                progress_bar.progress(100)
                status_text.text("generación completada")
                
                show_generation_result(result, concept, elapsed_time)
                
                st.session_state.generation_history.append({
                    'concept': concept,
                    'result': result,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'elapsed_time': elapsed_time
                })
                
            else:
                st.error(f"error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"error inesperado: {e}")
            import traceback
            with st.expander("ver detalles del error"):
                st.code(traceback.format_exc())

def show_generation_result(result, concept, elapsed_time):
    """muestro el resultado de la generación"""
    
    st.success("diagrama generado exitosamente")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("imagen generada")
        
        img_path = result['generation']['path']
        image = Image.open(img_path)
        
        st.image(image, use_container_width=True)
        
        with open(img_path, "rb") as file:
            st.download_button(
                label="descargar imagen",
                data=file,
                file_name=Path(img_path).name,
                mime="image/png"
            )
    
    with col2:
        st.subheader("reporte de calidad")
        
        validation = result['validation']
        
        st.metric(
            "tiempo de generación",
            f"{elapsed_time:.1f}s"
        )
        
        st.metric(
            "score de calidad",
            f"{validation['global_score']:.0%}",
            delta="aprobada" if validation['passed'] else "mejorable"
        )
        
        with st.expander("ver métricas detalladas"):
            show_quality_metrics(validation)
        
        if validation['recommendations']:
            st.markdown("recomendaciones")
            for rec in validation['recommendations']:
                st.info(rec)

def show_gallery_tab():
    """tab de galería de imágenes generadas"""
    
    st.subheader("galería de imágenes generadas")
    
    if not st.session_state.generation_history:
        st.info("no hay imágenes generadas aún")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sort_by = st.selectbox(
            "ordenar por:",
            ["Más recientes", "Mayor calidad", "Menor calidad"]
        )
    
    with col2:
        filter_quality = st.slider(
            "filtrar por calidad mínima:",
            0.0, 1.0, 0.0, 0.1
        )
    
    history = st.session_state.generation_history.copy()
    
    if sort_by == "Mayor calidad":
        history.sort(key=lambda x: x['result']['validation']['global_score'], reverse=True)
    elif sort_by == "Menor calidad":
        history.sort(key=lambda x: x['result']['validation']['global_score'])
    
    history = [h for h in history if h['result']['validation']['global_score'] >= filter_quality]
    
    if not history:
        st.warning("no hay imágenes que cumplan los filtros seleccionados")
        return
    
    cols_per_row = 3
    for i in range(0, len(history), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(history):
                item = history[i + j]
                
                with col:
                    img_path = item['result']['generation']['path']
                    image = Image.open(img_path)
                    st.image(image, use_container_width=True)
                    
                    quality = item['result']['validation']['global_score']
                    st.caption(f"{quality:.0%} | {item['elapsed_time']:.1f}s")
                    st.caption(f"{item['timestamp']}")
                    
                    with st.expander("ver concepto"):
                        st.write(item['concept'])

def show_statistics_tab():
    """tab de estadísticas"""
    
    st.subheader("estadísticas del sistema")
    
    if not st.session_state.generation_history:
        st.info("no hay estadísticas disponibles aún")
        return
    
    history = st.session_state.generation_history
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("total generadas", len(history))
    
    with col2:
        avg_quality = sum(h['result']['validation']['global_score'] for h in history) / len(history)
        st.metric("calidad promedio", f"{avg_quality:.0%}")
    
    with col3:
        approved = sum(1 for h in history if h['result']['validation']['passed'])
        st.metric("aprobadas", f"{approved}/{len(history)}")
    
    with col4:
        avg_time = sum(h['elapsed_time'] for h in history) / len(history)
        st.metric("tiempo promedio", f"{avg_time:.1f}s")
    
    st.markdown("evolución de calidad")
    
    import pandas as pd
    
    df = pd.DataFrame([
        {
            'generación': i + 1,
            'calidad': h['result']['validation']['global_score'],
            'tiempo': h['elapsed_time']
        }
        for i, h in enumerate(history)
    ])
    
    st.line_chart(df.set_index('generación')['calidad'])
    
    st.markdown("top 3 mejores imágenes")
    
    top_3 = sorted(history, key=lambda x: x['result']['validation']['global_score'], reverse=True)[:3]
    
    cols = st.columns(3)
    for i, (col, item) in enumerate(zip(cols, top_3)):
        with col:
            st.markdown(f"#{i+1}")
            img_path = item['result']['generation']['path']
            image = Image.open(img_path)
            st.image(image, use_container_width=True)
            st.caption(f"{item['result']['validation']['global_score']:.0%}")

if __name__ == "__main__":
    main()
