from src.cross_modal.cross_modal_coordinator import CrossModalCoordinator
from src.image_generation.advanced_image_generator import AdvancedImageGenerator

import streamlit as st
import sys
from pathlib import Path

st.set_page_config(
    page_title="Java API Knowledge System",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #f3e8ff;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    
    [data-testid="stSidebar"] * {
        color: #e5e5e5 !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        color: #7c3aed;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(124, 58, 237, 0.2);
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    with st.sidebar:
        st.markdown("# ☕ Java API Knowledge")
        st.markdown("---")
        
        page = st.radio(
            "Navegación",
            ["🏠 Inicio", "💬 Chat RAG", "🎨 Generador de Imágenes", "🔍 Exploración Visual"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 📊 Módulos")
        st.info("""
        **💬 Chat RAG**
        Sistema de preguntas y respuestas con Gemini
        
        **🎨 Generador de Imágenes**
        Creación de diagramas técnicos con IA
        
        **🔍 Exploración Visual**
        Clustering y análisis de documentos
        """)
    
    if page == "🏠 Inicio":
        show_home()
    elif page == "💬 Chat RAG":
        show_chat()
    elif page == "🎨 Generador de Imágenes":
        show_image_generation()
    elif page == "🔍 Exploración Visual":
        show_exploration()

def show_home():
    """Página de inicio"""
    st.markdown('<h1 class="main-header">☕ Java API Knowledge System</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; font-size: 1.2rem; color: #6b7280; margin-bottom: 3rem;">
        Sistema inteligente completo para documentación Java y Spring Boot
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 💬 Chat RAG
        
        Sistema de preguntas y respuestas inteligente usando:
        - ✨ Gemini 1.5 Flash
        - 🔍 Búsqueda semántica
        - 📚 Base de conocimiento Java/Spring
        
        **Características:**
        - Respuestas contextualizadas
        - Fuentes citadas
        - Historial de conversación
        """)
    
    with col2:
        st.markdown("""
        ### 🎨 Generador de Imágenes
        
        Creación de diagramas técnicos con IA:
        - 🖼️ Stable Diffusion 2.1
        - 🎯 8 tipos de diagramas
        - ✅ Validación automática
        
        **Características:**
        - Control de calidad con 7 métricas
        - 6 esquemas de color
        - Reintentos inteligentes
        """)
    
    with col3:
        st.markdown("""
        ### 🔍 Exploración Visual
        
        Análisis y clustering de documentos:
        - 📊 HDBSCAN / K-Means
        - 🗺️ Visualización 2D/3D
        - 📈 Estadísticas del corpus
        
        **Características:**
        - Reducción dimensional (UMAP)
        - Métricas de clustering
        - Exploración interactiva
        """)
    
    st.markdown("---")
    
    st.markdown("### 🚀 Comenzar")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Ir a Chat", use_container_width=True):
            st.session_state.page = "💬 Chat RAG"
            st.rerun()
    
    with col2:
        if st.button("🎨 Generar Imagen", use_container_width=True):
            st.session_state.page = "🎨 Generador de Imágenes"
            st.rerun()
    
    with col3:
        if st.button("🔍 Explorar Datos", use_container_width=True):
            st.session_state.page = "🔍 Exploración Visual"
            st.rerun()
    
    # Estadísticas del sistema
    st.markdown("---")
    st.markdown("### 📊 Estadísticas del Sistema")
    
    try:
        sys.path.append(str(Path(__file__).parent.parent / "src"))
        from storage.vector_store import VectorStore
        
        vector_store = VectorStore()
        doc_count = vector_store.get_document_count()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Documentos", doc_count)
        with col2:
            st.metric("Modelo Embeddings", "MiniLM-L6")
        with col3:
            st.metric("Dimensiones", "384")
        with col4:
            st.metric("Base de Datos", "ChromaDB")
            
    except:
        st.info("Sistema inicializándose...")

def show_chat():
    """Página de chat RAG con integración cross-modal"""
    sys.path.append(str(Path(__file__).parent.parent / "src"))
    
    import os
    from dotenv import load_dotenv
    import random
    
    load_dotenv()
    
    from search.semantic_search import SemanticSearch
    from storage.vector_store import VectorStore
    from embeddings.embedding_engine import EmbeddingEngine
    from chat.rag_engine import RAGEngine
    
    st.markdown('<h1 class="main-header">💬 Chat con Documentación Java/Spring</h1>', unsafe_allow_html=True)

    @st.cache_resource
    def init_cross_modal_components():
        vector_store = VectorStore()
        embedding_engine = EmbeddingEngine()
        search_engine = SemanticSearch(vector_store, embedding_engine)
        rag_engine = RAGEngine(search_engine, api_key=os.getenv("GEMINI_API_KEY"))

        image_generator = AdvancedImageGenerator(
            api_key=os.getenv("STABILITY_API_KEY"),
            output_dir="data/generated_images"
        )

        coordinator = CrossModalCoordinator(rag_engine, image_generator)

        return coordinator
    
    coordinator = init_cross_modal_components()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        top_k = st.slider("Documentos a consultar", 1, 10, 3)
        
        # botón para limpiar historial
        if st.button("🗑️ Limpiar Historial", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Mensajes
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    CUTE_EMOJIS = ["🦄", "🌸", "🎀", "🌙", "💝", "🧸", "🍓", "🦋"]
    
    # Renderizar historial de mensajes
    for message in st.session_state.messages:
        avatar = message.get("avatar", "✨" if message["role"] == "assistant" else random.choice(CUTE_EMOJIS))
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            
            if message.get("image_path"):
                try:
                    image_path = Path(message["image_path"])
                    if image_path.exists():
                        st.image(str(image_path), caption="Diagrama generado", use_column_width=True)
                    else:
                        st.error(f"Imagen no encontrada: {message['image_path']}")
                except Exception as e:
                    st.error(f"Error al cargar imagen: {e}")
            
            if message.get("sources"):
                st.markdown("---")
                st.markdown("**Fuentes:**")
                for source in message["sources"]:
                    st.markdown(f'🔗 {source["title"]} (similaridad: {source["score"]:.2f})')
    
    if prompt := st.chat_input("Pregunta sobre Java/Spring Boot"):
        user_emoji = random.choice(CUTE_EMOJIS)
        
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "avatar": user_emoji
        })
        
        with st.chat_message("user", avatar=user_emoji):
            st.write(prompt)
        
        with st.chat_message("assistant", avatar="✨"):
            with st.spinner("Generando respuesta..."):
                result = coordinator.process_cross_modal_query(prompt, top_k=top_k)

                if result.get('filter_blocked'):
                    st.error("contenido bloqueado")
                    st.warning(result.get('filter_reason', 'la consulta contiene contenido inapropiado'))
                    st.stop()
                
                if result.get("text_answer"):
                    st.markdown(result["text_answer"])
                elif result.get("modality") == "image_only":
                    st.info("📊 He generado un diagrama visual para tu pregunta:")

                if result.get("image_generated") and result.get("image_path"):
                    try:
                        image_path = Path(result["image_path"])
                        
                        if image_path.exists():
                            absolute_path = image_path.resolve()
                            st.image(str(absolute_path), caption="Diagrama generado", use_column_width=True)
                        else:
                            st.error(f"La imagen se generó pero no se encuentra en: {image_path}")
                            st.info("Verifica que la carpeta 'data/generated_images/' exista")
                    except Exception as e:
                        st.error(f" Error al mostrar la imagen: {str(e)}")
                        st.code(f"Ruta de imagen: {result.get('image_path')}")
                
                # Mostrar fuentes si existen
                if result.get("sources"):
                    st.markdown("---")
                    st.markdown("**Fuentes:**")
                    for source in result["sources"]:
                        st.markdown(f'🔗 {source["title"]} (similaridad: {source["score"]:.2f})')
                
                assistant_content = result["text_answer"] if result.get("text_answer") else "📊 Diagrama generado"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_content,
                    "image_path": result.get("image_path"),  # Guardar ruta completa
                    "sources": result.get("sources", [])
                })

def show_image_generation():
    """Página de generación de imágenes"""
    from ui.pages.image_generation_page import main as image_gen_main
    image_gen_main()

def show_exploration():
    """Página de exploración visual"""
    from ui.pages.exploration_page import show_exploration_page
    show_exploration_page()

if __name__ == "__main__":
    main()