"""
FastAPI Main Application
REST API for Tradl News Intelligence System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_orchestrator import TradlOrchestrator
from utils.business_metrics import BusinessMetricsCalculator

# Initialize FastAPI app
app = FastAPI(
    title="Tradl News Intelligence API",
    description="AI-Powered Financial News Processing System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system
orchestrator = None
business_calc = BusinessMetricsCalculator()

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global orchestrator
    print("🚀 Starting Tradl API...")
    orchestrator = TradlOrchestrator()
    print("✅ System ready!")

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class Article(BaseModel):
    """Article input model"""
    title: str
    content: str
    source: str
    date: str
    id: Optional[str] = None
    url: Optional[str] = None

class ProcessRequest(BaseModel):
    """Process news request"""
    articles: List[Article]

class QueryRequest(BaseModel):
    """Query request"""
    query: str
    top_k: Optional[int] = 10
    explain: Optional[bool] = True

class ProcessResponse(BaseModel):
    """Process response"""
    success: bool
    processed: int
    stored: int
    duplicates: int
    errors: int
    message: str

class QueryResponse(BaseModel):
    """Query response"""
    success: bool
    query: str
    total_found: int
    results: List[Dict]

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Tradl News Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "process": "/api/process",
            "query": "/api/query",
            "stats": "/api/stats",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    stats = orchestrator.get_system_stats()
    
    return {
        "status": "healthy",
        "system": "operational",
        "articles_in_db": stats['vector_store']['total_articles'],
        "knowledge_graph_nodes": stats['knowledge_graph']['total_nodes']
    }

@app.post("/api/process", response_model=ProcessResponse)
async def process_news(request: ProcessRequest):
    """Process news articles through the pipeline"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Convert Pydantic models to dicts
        articles = [article.dict() for article in request.articles]
        
        # Process through orchestrator
        result = orchestrator.process_news(articles)
        
        return ProcessResponse(
            success=True,
            processed=result['processed'],
            stored=result['stored'],
            duplicates=result['duplicates'],
            errors=result['errors'],
            message=f"Successfully processed {result['stored']} unique articles"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/api/query", response_model=QueryResponse)
async def query_news(request: QueryRequest):
    """Query the news database"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        result = orchestrator.query_news(
            query=request.query,
            top_k=request.top_k,
            explain=request.explain
        )
        
        return QueryResponse(
            success=True,
            query=request.query,
            total_found=len(result['results']),
            results=result['results']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        system_stats = orchestrator.get_system_stats()
        
        return {
            "success": True,
            "system_stats": system_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")