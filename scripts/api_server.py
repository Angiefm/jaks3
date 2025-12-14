import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException  
from pydantic import BaseModel  
from typing import List, Optional  
import sys  

load_dotenv()
sys.path.append('src')  

  
from chat.rag_engine import RAGEngine  
from search.semantic_search import SemanticSearch  
from storage.vector_store import VectorStore  
from embeddings.embedding_engine import EmbeddingEngine  
from image_generation.advanced_image_generator import AdvancedImageGenerator  
  
app = FastAPI(title="Java Knowledge System API", version="1.0.0")  
  
class ChatRequest(BaseModel):  
    question: str  
    top_k: int = 3  
  
class ChatResponse(BaseModel):  
    answer: str  
    sources: List[dict]  
  
class ImageRequest(BaseModel):  
    concept: str  
    style: Optional[str] = None  
  
class ImageResponse(BaseModel):  
    success: bool  
    image_path: Optional[str] = None  
    error: Optional[str] = None  
  
vector_store = VectorStore()  
embedding_engine = EmbeddingEngine()  
search_engine = SemanticSearch(vector_store, embedding_engine)  
rag_engine = RAGEngine(search_engine, api_key=os.getenv("GEMINI_API_KEY"))  
image_generator = AdvancedImageGenerator(api_key=os.getenv("STABILITY_API_KEY"))  
  
@app.get("/")  
async def root():  
    return {"message": "Java Knowledge System API"}  
  
@app.get("/health")  
async def health_check():  
    return {"status": "healthy"}  
  
@app.post("/chat", response_model=ChatResponse)  
async def chat(request: ChatRequest):  
    try:  
        result = rag_engine.generate_answer(request.question, top_k=request.top_k)  
        return ChatResponse(answer=result["answer"], sources=result["sources"])  
    except Exception as e:  
        raise HTTPException(status_code=500, detail=str(e))  
  
@app.post("/generate-image", response_model=ImageResponse)  
async def generate_image(request: ImageRequest):  
    try:  
        result = image_generator.generate_with_quality_check(request.concept)  
        if result.get('success'):  
            return ImageResponse(success=True, image_path=result['generation']['path'])  
        else:  
            return ImageResponse(success=False, error=result.get('error', 'Unknown error'))  
    except Exception as e:  
        raise HTTPException(status_code=500, detail=str(e))  
  
@app.get("/system/info")  
async def system_info():  
    return {  
        "components": {  
            "chat_engine": "Gemini 1.5 Flash",  
            "image_generator": "Stability AI SDXL",  
            "vector_db": "ChromaDB",  
            "embedding_model": "MiniLM-L6-v2"  
        },  
        "status": "operational"  
    }