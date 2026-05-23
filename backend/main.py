from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import shutil
from datetime import datetime
import io

from config import settings
from knowledge_base import KnowledgeBase
from llm_api import LLMClient
from document_exporter import DocumentExporter

app = FastAPI(
    title="BucengRAG API",
    description="不曾社科理论RAG分析系统 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kb: Optional[KnowledgeBase] = None
llm_client: Optional[LLMClient] = None
exporter = DocumentExporter()


class AnalyzeRequest(BaseModel):
    event_text: str
    analysis_mode: str = "minecraft"
    temperature: Optional[float] = None
    thinking_enabled: bool = True
    reasoning_effort: str = "high"
    max_results: int = 5


class AddCardRequest(BaseModel):
    title: str
    content: str
    category: str = "general"
    keywords: List[str] = []
    source: str = ""


class SearchRequest(BaseModel):
    query: str
    k: int = 5


@app.on_event("startup")
async def startup_event():
    global kb, llm_client
    
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    kb = KnowledgeBase()
    
    seed_files = [
        "seed_cards.json",
        "social_theory_cards.json",
        "general_social_theory_cards.json",
        "marxism_leninism_mao_cards.json",
        "human_civilization_history.json"
    ]
    
    for seed_file in seed_files:
        file_path = os.path.join(data_dir, seed_file)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                cards = json.load(f)
                if isinstance(cards, list):
                    kb.add_cards(cards)
    
    try:
        llm_client = LLMClient()
    except Exception as e:
        print(f"LLM client initialization warning: {e}")


@app.get("/")
async def root():
    return {"message": "BucengRAG API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "kb_initialized": kb is not None,
        "llm_initialized": llm_client is not None
    }


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    if not kb:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")
    
    try:
        retrieved_cards = kb.search(request.event_text, k=request.max_results)
        
        history_records = []
        if hasattr(kb, 'search_history'):
            history_records = kb.search_history(request.event_text, k=settings.MAX_HISTORY_RESULTS)
        
        if llm_client:
            analysis = llm_client.generate_analysis(
                event_text=request.event_text,
                retrieved_cards=retrieved_cards,
                temperature=request.temperature,
                analysis_mode=request.analysis_mode,
                history_records=history_records,
                thinking_enabled=request.thinking_enabled,
                reasoning_effort=request.reasoning_effort
            )
        else:
            analysis = "LLM client not initialized. Please check API key configuration."
        
        return {
            "analysis": analysis,
            "retrieved_cards": retrieved_cards,
            "history_records": history_records,
            "model": settings.LLM_MODEL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search_cards(request: SearchRequest):
    if not kb:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")
    
    try:
        results = kb.search(request.query, k=request.k)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cards")
async def list_cards(category: Optional[str] = None, limit: int = 100):
    if not kb:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")
    
    try:
        cards = kb.get_all_cards(limit=limit)
        if category:
            cards = [c for c in cards if c.get("category") == category]
        return {"cards": cards, "count": len(cards)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cards")
async def add_card(request: AddCardRequest):
    if not kb:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")
    
    try:
        card = {
            "id": f"card_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": request.title,
            "content": request.content,
            "category": request.category,
            "keywords": request.keywords,
            "source": request.source,
            "created_at": datetime.now().isoformat()
        }
        kb.add_cards([card])
        return {"message": "Card added successfully", "card": card}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cards/{card_id}")
async def delete_card(card_id: str):
    if not kb:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")
    
    try:
        kb.delete_card(card_id)
        return {"message": "Card deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not kb:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")
    
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        cards = []
        if file.filename.endswith('.json'):
            with open(temp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    cards = data
        elif file.filename.endswith('.jsonl'):
            with open(temp_path, "r", encoding="utf-8") as f:
                cards = [json.loads(line) for line in f if line.strip()]
        
        if cards:
            kb.add_cards(cards)
        
        os.remove(temp_path)
        return {"message": f"Processed {len(cards)} cards from document"}
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/markdown")
async def export_markdown(request: AnalyzeRequest):
    if not kb:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")
    
    try:
        retrieved_cards = kb.search(request.event_text, k=request.max_results)
        
        if llm_client:
            analysis = llm_client.generate_analysis(
                event_text=request.event_text,
                retrieved_cards=retrieved_cards,
                temperature=request.temperature,
                analysis_mode=request.analysis_mode
            )
        else:
            analysis = "LLM client not initialized."
        
        md_content = exporter.export_to_markdown(
            event_text=request.event_text,
            analysis=analysis,
            retrieved_cards=retrieved_cards,
            llm_model=settings.LLM_MODEL
        )
        
        return StreamingResponse(
            iter([md_content]),
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    if not kb:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")
    
    try:
        cards = kb.get_all_cards(limit=10000)
        categories = {}
        for card in cards:
            cat = card.get("category", "uncategorized")
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_cards": len(cards),
            "categories": categories,
            "embedding_model": settings.EMBEDDING_MODEL,
            "llm_model": settings.LLM_MODEL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
