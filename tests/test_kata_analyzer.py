# tests/test_kata_analyzer.py

import pytest
from datetime import datetime, timedelta
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.analysis.analyzer import KataAnalyzer, KataMetrics, KataStatus, KataAnalysis
from app.llm.types import ResponseType, LLMResponse
from app.vectorstore.vector_store import VectorStore
from app.orchestrator.orchestrator import RAGOrchestrator



@pytest.fixture
def mock_orchestrator():
    orchestrator = Mock(spec=RAGOrchestrator)
    orchestrator.process_query = AsyncMock()
    return orchestrator

@pytest.fixture
def mock_vector_store():
    vector_store = Mock(spec=VectorStore)
    vector_store.vectorizer.vectorize = AsyncMock(return_value=np.array([[1.0, 0.0, 0.0]]))
    return vector_store

@pytest.fixture
def analyzer(mock_orchestrator, mock_vector_store):
    return KataAnalyzer(
        orchestrator=mock_orchestrator,
        vector_store=mock_vector_store
    )

@pytest.fixture
def sample_project_data():
    """Proporciona datos de ejemplo de un proyecto Kata"""
    current_date = datetime.utcnow()
    return {
        "process": {
            "id": "P001",
            "description": "Proceso de mejora continua"
        },
        "tribe": {
            "id": "T001",
            "name": "Equipo Innovación"
        },
        "challenge": {
            "id": "C001",
            "description": "Reducir tiempo de ciclo en 50%"
        },
        "actual_state": {
            "metrics": {"cycle_time": 10}
        },
        "target_state": {
            "metrics": {"cycle_time": 5}
        },
        "obstacles": [
            {
                "id": "O001",
                "description": "Falta de automatización",
                "status": "in_progress",
                "impact_level": 4
            }
        ],
        "hypotheses": [
            {
                "id": "H001",
                "description": "Automatizar proceso X reducirá tiempo",
                "validated": True
            }
        ],
        "experiments": [
            {
                "id": "E001",
                "description": "Implementar automatización en proceso X",
                "start_date": (current_date - timedelta(days=10)).isoformat(),
                "end_date": current_date.isoformat(),
                "methodology": "PDCA",
                "goals": "Reducir tiempo manual",
                "results": {"success": True}
            }
        ],
        "learnings": [
            {
                "id": "L001",
                "description": "La automatización redujo tiempo en 30%",
                "learning_date": current_date.isoformat(),
                "actionable_items": ["Extender automatización a otros procesos"]
            }
        ],
        "mental_contrast": {
            "points": 8,
            "evaluation_date": current_date.isoformat()
        }
    }

# Tests para el análisis principal
@pytest.mark.asyncio
async def test_analyze_project(analyzer, sample_project_data):
    """Test del análisis completo de un proyecto"""
    # Mock para _fetch_project_data
    analyzer._fetch_project_data = AsyncMock(return_value=sample_project_data)
    
    # Mock para respuestas del LLM
    mock_llm_response = LLMResponse(
        content="Insight 1\nInsight 2",
        metadata={},
        confidence=0.9
    )
    analyzer.orchestrator.process_query.return_value = mock_llm_response

    # Ejecutar análisis
    analysis = await analyzer.analyze_project("P001")

    # Verificar resultado
    assert isinstance(analysis, KataAnalysis)
    assert analysis.project_id == "P001"
    assert isinstance(analysis.metrics, KataMetrics)
    assert isinstance(analysis.status, KataStatus)
    assert len(analysis.insights) > 0
    assert len(analysis.recommendations) > 0

# Tests para cálculo de métricas
@pytest.mark.asyncio
async def test_calculate_metrics(analyzer, sample_project_data):
    """Test del cálculo de métricas"""
    metrics = await analyzer._calculate_metrics(sample_project_data)
    
    assert isinstance(metrics, KataMetrics)
    assert 0 <= metrics.process_adherence <= 1
    assert metrics.experiment_cycle_time >= 0
    assert 0 <= metrics.learning_quality <= 1
    assert 0 <= metrics.obstacle_resolution_rate <= 1
    assert 0 <= metrics.hypothesis_validation_rate <= 1
    assert 0 <= metrics.target_achievement <= 1
    assert 0 <= metrics.mental_contrast_score <= 1

def test_calculate_process_adherence(analyzer, sample_project_data):
    """Test del cálculo de adherencia al proceso"""
    adherence = analyzer._calculate_process_adherence(
        sample_project_data["experiments"],
        sample_project_data["learnings"]
    )
    
    assert 0 <= adherence <= 1

def test_calculate_experiment_cycle_time(analyzer, sample_project_data):
    """Test del cálculo de tiempo de ciclo de experimentos"""
    cycle_time = analyzer._calculate_experiment_cycle_time(
        sample_project_data["experiments"]
    )
    
    assert cycle_time >= 0
    assert cycle_time == 10  # Basado en los datos de ejemplo

# Tests para evaluación de estado
@pytest.mark.asyncio
async def test_evaluate_status(analyzer, sample_project_data):
    """Test de la evaluación de estado"""
    metrics = await analyzer._calculate_metrics(sample_project_data)
    status = await analyzer._evaluate_status(sample_project_data, metrics)
    
    assert isinstance(status, KataStatus)
    assert status.status in ["on_track", "needs_adjustment", "at_risk"]
    assert isinstance(status.coaching_needs, list)
    assert isinstance(status.blocking_obstacles, list)
    assert isinstance(status.next_experiments, list)
    assert isinstance(status.risk_factors, list)

def test_identify_blocking_obstacles(analyzer, sample_project_data):
    """Test de identificación de obstáculos bloqueantes"""
    blocking = analyzer._identify_blocking_obstacles(
        sample_project_data["obstacles"]
    )
    
    assert isinstance(blocking, list)
    assert len(blocking) > 0
    assert all(isinstance(o, dict) for o in blocking)
    assert all("impact" in o for o in blocking)

# Tests para generación de insights y recomendaciones
@pytest.mark.asyncio
async def test_generate_insights(analyzer, sample_project_data):
    """Test de generación de insights"""
    metrics = await analyzer._calculate_metrics(sample_project_data)
    
    # Mock respuesta del LLM
    mock_response = LLMResponse(
        content="Insight 1\nInsight 2\nInsight 3",
        metadata={},
        confidence=0.9
    )
    analyzer.orchestrator.process_query.return_value = mock_response
    
    insights = await analyzer._generate_insights(sample_project_data, metrics)
    
    assert isinstance(insights, list)
    assert len(insights) > 0
    assert all(isinstance(i, str) for i in insights)

@pytest.mark.asyncio
async def test_generate_recommendations(analyzer, sample_project_data):
    """Test de generación de recomendaciones"""
    metrics = await analyzer._calculate_metrics(sample_project_data)
    status = await analyzer._evaluate_status(sample_project_data, metrics)
    
    # Mock respuesta del LLM
    mock_response = LLMResponse(
        content="Acción: Mejorar automatización\nPrioridad: alta\nImpacto: Alto\nTiempo: 1 semana",
        metadata={},
        confidence=0.9
    )
    analyzer.orchestrator.process_query.return_value = mock_response
    
    recommendations = await analyzer._generate_recommendations(
        sample_project_data,
        metrics,
        status
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert all(isinstance(r, dict) for r in recommendations)
    assert all("action" in r for r in recommendations)

# Tests para métodos auxiliares
@pytest.mark.asyncio
async def test_calculate_semantic_similarity(analyzer):
    """Test de cálculo de similitud semántica"""
    similarity = await analyzer._calculate_semantic_similarity(
        "Automatizar proceso",
        "Proceso de automatización"
    )
    
    assert 0 <= similarity <= 1

def test_evaluate_actionability(analyzer):
    """Test de evaluación de accionabilidad"""
    action_items = [
        "Implementar sistema automatizado",
        "Medir tiempo de proceso",
        "Evaluar resultados semanalmente"
    ]
    
    score = analyzer._evaluate_actionability(action_items)
    assert 0 <= score <= 1

# Tests de error handling
@pytest.mark.asyncio
async def test_error_handling_in_analysis(analyzer):
    """Test de manejo de errores en análisis"""
    analyzer._fetch_project_data = AsyncMock(side_effect=Exception("Error de prueba"))
    
    with pytest.raises(Exception):
        await analyzer.analyze_project("P001")