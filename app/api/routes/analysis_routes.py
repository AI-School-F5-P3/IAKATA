from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

from app.analysis.analyzer import KataAnalyzer, ProjectAnalysis
from app.orchestrator.orchestrator import RAGOrchestrator
from app.vectorstore.vector_store import VectorStore
from app.analysis.db_connector import AnalysisDBConnector

# Configura el router
router = APIRouter()
logger = logging.getLogger(__name__)

# Dependencia para obtener el analizador
async def get_analyzer():
    """Dependencia para obtener la instancia del analizador"""
    from app.api.services.chat_services import get_components
    
    components = get_components()
    orchestrator = components["orchestrator"]
    vector_store = components["vector_store"]
    
    db_connector = AnalysisDBConnector()
    
    analyzer = KataAnalyzer(
        orchestrator=orchestrator,
        vector_store=vector_store,
        db_connector=db_connector
    )
    
    return analyzer

@router.get("/projects/{project_id}", response_model=ProjectAnalysis)
async def analyze_project(
    project_id: str,
    refresh: bool = Query(False, description="Forzar nuevo análisis ignorando caché"),
    time_range: Optional[str] = Query("7d", regex="^\d+[dwm]$", 
                                    description="Rango temporal para análisis (ej: 7d, 2w, 1m)"),
    analyzer: KataAnalyzer = Depends(get_analyzer)
) -> Dict:
    """
    Analiza un proyecto Lean Kata y retorna métricas, insights y recomendaciones
    
    Args:
        project_id: ID del proyecto a analizar
        refresh: Si es True, fuerza un nuevo análisis ignorando caché
        time_range: Rango temporal para el análisis de tendencias
        
    Returns:
        Objeto ProjectAnalysis con el análisis completo
    """
    try:
        # Convertir time_range a objeto timedelta
        time_units = {"d": "days", "w": "weeks", "m": "months"}
        unit = time_range[-1]
        value = int(time_range[:-1])
        
        analysis = await analyzer.analyze_project(
            project_id, 
            refresh_cache=refresh,
            time_delta=timedelta(**{time_units[unit]: value})
            
        )
        # Convertir trend en objeto para compatibilidad con el frontend
        trend_info = {
            "direction": analysis.trend(),
            "velocity": "normal",
            "confidence": 0.8
        }
        
        # Conversión para respuesta API
        return {
            "project_id": analysis.project_id,
            "project_name": analysis.project_name,
            "metrics": analysis.metrics.to_display_dict(),
            "status": {
                "status": analysis.status.status,
                "coaching_needs": analysis.status.coaching_needs,
                "blocking_obstacles": analysis.status.blocking_obstacles,
                "risk_factors": analysis.status.risk_factors
            },
            "insights": [
                {
                    "type": insight.type,
                    "description": insight.description,
                    "importance": insight.importance,
                    "related_metric": insight.related_metric
                }
                for insight in analysis.insights
            ],
            "recommendations": [
                {
                    "action": rec.action,
                    "priority": rec.priority,
                    "impact": rec.impact,
                    "estimated_time": rec.estimated_time
                }
                for rec in analysis.recommendations
            ],
            "trend": {
                "direction": analysis.trend.direction,
                "velocity": analysis.trend.velocity,
                "confidence": analysis.trend.confidence
            },
            "analyzed_at": analysis.analyzed_at.isoformat(),
            "next_review": analysis.next_review.isoformat() if analysis.next_review else None
        }
        
    except ValueError as ve:
        logger.error(f"Error de validación: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error en análisis del proyecto {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al analizar el proyecto: {str(e)}"
        )