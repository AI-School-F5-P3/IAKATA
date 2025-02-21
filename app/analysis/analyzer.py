# app/analysis/analyzer.py

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field
import numpy as np

from app.llm.types import ResponseType, LLMResponse
from app.orchestrator.orchestrator import RAGOrchestrator
from app.vectorstore.vector_store import VectorStore
from app.retriever.types import BoardSection, SearchQuery, FilterConfig

# Importar modelos de LK-WEB
from app.models.ProcessModel import ProcessModel
from app.models.TribeModel import TribeModel
from app.models.ChallengeModel import ChallengeModel
from app.models.ActualStateModel import ActualStateModel
from app.models.TargetStateModel import TargetStateModel
from app.models.ObstacleModel import ObstacleModel
from app.models.HypothesisModel import HypothesisModel
from app.models.ExperimentModel import ExperimentModel
from app.models.TaskModel import TaskModel
from app.models.ResultsModel import ResultsModel
from app.models.LearningsModel import LearningModel
from app.models.MentalContrastModel import MentalContrastModel

class KataMetrics(BaseModel):

    """Métricas específicas de Lean Kata"""
    process_adherence: float = Field(..., description="Adherencia al proceso Kata (0-1)")
    experiment_cycle_time: float = Field(..., description="Tiempo medio del ciclo PDCA en días")
    learning_quality: float = Field(..., description="Calidad de aprendizajes (0-1)")
    obstacle_resolution_rate: float = Field(..., description="Tasa de resolución de obstáculos")
    hypothesis_validation_rate: float = Field(..., description="Tasa de validación de hipótesis")
    target_achievement: float = Field(..., description="Progreso hacia el estado objetivo")
    mental_contrast_score: float = Field(..., description="Puntuación del contraste mental")

class KataStatus(BaseModel):

    """Estado actual del proyecto Kata"""
    status: str = Field(..., description="Estado global: on_track, needs_adjustment, at_risk")
    coaching_needs: List[str] = Field(default_factory=list, description="Áreas que necesitan coaching")
    blocking_obstacles: List[Dict] = Field(default_factory=list, description="Obstáculos bloqueantes")
    next_experiments: List[Dict] = Field(default_factory=list, description="Próximos experimentos sugeridos")
    risk_factors: List[str] = Field(default_factory=list, description="Factores de riesgo identificados")

class KataAnalysis(BaseModel):

    """Análisis completo del proyecto Kata"""
    project_id: str
    metrics: KataMetrics
    status: KataStatus
    insights: List[str]
    recommendations: List[Dict[str, Any]]
    timestamp: datetime

class KataAnalyzer:
    def __init__(
        self,
        orchestrator: RAGOrchestrator,
        vector_store: VectorStore,
        update_interval: int = 3600
    ):
        self.orchestrator = orchestrator
        self.vector_store = vector_store
        self.update_interval = update_interval
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._last_update = {}

    async def analyze_project(self, project_id: str) -> KataAnalysis:

        """Analiza un proyecto Lean Kata completo"""

        try:
            if self._is_cache_valid(project_id):
                return self._cache[project_id]

            # Obtener datos del proyecto
            project_data = await self._fetch_project_data(project_id)
            
            # Calcular métricas
            metrics = await self._calculate_metrics(project_data)
            
            # Evaluar estado
            status = await self._evaluate_status(project_data, metrics)
            
            # Generar insights
            insights = await self._generate_insights(project_data, metrics)
            
            # Generar recomendaciones
            recommendations = await self._generate_recommendations(project_data, metrics, status)

            analysis = KataAnalysis(
                project_id=project_id,
                metrics=metrics,
                status=status,
                insights=insights,
                recommendations=recommendations,
                timestamp=datetime.utcnow()
            )

            self._update_cache(project_id, analysis)
            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing project {project_id}: {str(e)}")
            raise

    async def _fetch_project_data(self, project_id: str) -> Dict:

        """Obtiene datos completos del proyecto desde LK-WEB"""

        try:
            # Obtener proceso y tribu
            process = await ProcessModel.findByPk(project_id)
            if not process:
                raise ValueError(f"Process not found: {project_id}")
                
            tribe = await TribeModel.findOne({
                "where": {"process_id": process.id}
            })
            
            # Obtener reto y estados
            challenge = await ChallengeModel.findOne({
                "where": {"tribe_id": tribe.id}
            })
            
            actual_state = await ActualStateModel.findOne({
                "where": {"challenge_id": challenge.id}
            })
            
            target_state = await TargetStateModel.findOne({
                "where": {"challenge_id": challenge.id}
            })
            
            # Obtener elementos de experimentación
            obstacles = await ObstacleModel.findAll({
                "where": {"target_state_id": target_state.id}
            })
            
            obstacle_ids = [o.id for o in obstacles]
            hypotheses = await HypothesisModel.findAll({
                "where": {"obstacle_id": {"in": obstacle_ids}}
            })
            
            hypothesis_ids = [h.id for h in hypotheses]
            experiments = await ExperimentModel.findAll({
                "where": {"hypothesis_id": {"in": hypothesis_ids}}
            })
            
            # Obtener tareas y resultados
            experiment_ids = [e.id for e in experiments]
            tasks = await TaskModel.findAll({
                "where": {"experiment_id": {"in": experiment_ids}}
            })
            
            results = await ResultsModel.findAll({
                "where": {"experiment_id": {"in": experiment_ids}}
            })
            
            # Obtener aprendizajes
            result_ids = [r.id for r in results]
            learnings = await LearningModel.findAll({
                "where": {"results_id": {"in": result_ids}}
            })
            
            # Obtener contraste mental
            mental_contrast = await MentalContrastModel.findOne({
                "where": {"target_state_id": target_state.id}
            })

            return {
                "process": process,
                "tribe": tribe,
                "challenge": challenge,
                "actual_state": actual_state,
                "target_state": target_state,
                "obstacles": obstacles,
                "hypotheses": hypotheses,
                "experiments": experiments,
                "tasks": tasks,
                "results": results,
                "learnings": learnings,
                "mental_contrast": mental_contrast
            }

        except Exception as e:
            self.logger.error(f"Error fetching project data: {str(e)}")
            raise

    def _is_cache_valid(self, project_id: str) -> bool:

        """Verifica si el caché para un proyecto es válido"""

        if project_id not in self._last_update:
            return False
        time_since_update = (datetime.utcnow() - self._last_update[project_id]).total_seconds()
        return time_since_update < self.update_interval

    def _update_cache(self, project_id: str, analysis: KataAnalysis):
        """Actualiza el caché con un nuevo análisis"""
        self._cache[project_id] = analysis
        self._last_update[project_id] = datetime.utcnow()

    async def _calculate_metrics(self, project_data: Dict) -> KataMetrics:
        """Calcula métricas del proyecto Kata"""
        try:
            # Calcular adherencia al proceso
            process_adherence = self._calculate_process_adherence(
                project_data["experiments"],
                project_data["learnings"]
            )

            # Calcular tiempo de ciclo de experimentos
            cycle_time = self._calculate_experiment_cycle_time(
                project_data["experiments"]
            )

            # Evaluar calidad de aprendizajes
            learning_quality = await self._evaluate_learning_quality(
                project_data["learnings"],
                project_data["experiments"]
            )

            # Calcular tasa de resolución de obstáculos
            obstacle_rate = self._calculate_obstacle_resolution_rate(
                project_data["obstacles"]
            )

            # Calcular tasa de validación de hipótesis
            hypothesis_rate = self._calculate_hypothesis_validation_rate(
                project_data["hypotheses"]
            )

            # Calcular progreso hacia objetivo
            target_achievement = self._calculate_target_achievement(
                project_data["actual_state"],
                project_data["target_state"]
            )

            # Calcular score de contraste mental
            mental_score = self._calculate_mental_contrast_score(
                project_data["mental_contrast"]
            )

            return KataMetrics(
                process_adherence=process_adherence,
                experiment_cycle_time=cycle_time,
                learning_quality=learning_quality,
                obstacle_resolution_rate=obstacle_rate,
                hypothesis_validation_rate=hypothesis_rate,
                target_achievement=target_achievement,
                mental_contrast_score=mental_score
            )

        except Exception as e:
            self.logger.error(f"Error calculating metrics: {str(e)}")
            raise

    def _calculate_process_adherence(
        self,
        experiments: List[Dict],
        learnings: List[Dict]
    ) -> float:
        
        """Calcula la adherencia al proceso Kata basado en la calidad de experimentos y aprendizajes"""

        if not experiments:
            return 0.0

        # Criterios de adherencia
        criteria_scores = []

        # 1. Ciclo PDCA completo en experimentos
        for exp in experiments:
            score = 0
            # Plan
            if exp.get("methodology") and exp.get("goals"):
                score += 0.25
            # Do
            if exp.get("execution_details"):
                score += 0.25
            # Check
            if exp.get("results_obtained"):
                score += 0.25
            # Act
            if exp.get("next_steps"):
                score += 0.25
            criteria_scores.append(score)

        # 2. Calidad de aprendizajes
        learning_scores = []
        for learning in learnings:
            score = 0
            # Descripción clara
            if len(learning.get("description", "").strip()) > 50:
                score += 0.3
            # Acciones específicas
            if learning.get("actionable_items"):
                score += 0.4
            # Vinculación con próximos pasos
            if learning.get("next_steps"):
                score += 0.3
            learning_scores.append(score)

        # Calcular score final (60% experimentos, 40% aprendizajes)
        exp_score = np.mean(criteria_scores) if criteria_scores else 0
        learn_score = np.mean(learning_scores) if learning_scores else 0

        return (exp_score * 0.6) + (learn_score * 0.4)

    def _calculate_experiment_cycle_time(self, experiments: List[Dict]) -> float:

        """Calcula el tiempo promedio del ciclo PDCA en días"""

        if not experiments:
            return 0.0

        cycle_times = []
        for exp in experiments:
            start_date = exp.get("start_date")
            end_date = exp.get("end_date")
            
            if start_date and end_date:
                try:
                    start = datetime.fromisoformat(start_date)
                    end = datetime.fromisoformat(end_date)
                    duration = (end - start).days
                    # Solo considerar ciclos menores a 30 días
                    if 0 < duration <= 30:
                        cycle_times.append(duration)
                except ValueError:
                    continue

        return np.mean(cycle_times) if cycle_times else 0.0

    async def _evaluate_learning_quality(
        self,
        learnings: List[Dict],
        experiments: List[Dict]
    ) -> float:
        
        """Evalúa la calidad de los aprendizajes usando el RAG para análisis semántico"""
        
        if not learnings:
            return 0.0

        quality_scores = []
        for learning in learnings:
            score = 0
            description = learning.get("description", "")
            
            # 1. Completitud (30%)
            if len(description) > 100:
                score += 0.3
            elif len(description) > 50:
                score += 0.15

            # 2. Vinculación con experimentos (30%)
            exp_id = learning.get("experiment_id")
            if exp_id:
                related_exp = next((e for e in experiments if e["id"] == exp_id), None)
                if related_exp:
                    # Análisis semántico de relevancia
                    similarity = await self._calculate_semantic_similarity(
                        description,
                        related_exp.get("hypothesis", "")
                    )
                    score += similarity * 0.3

            # 3. Accionabilidad (40%)
            if learning.get("actionable_items"):
                actionable_score = self._evaluate_actionability(
                    learning["actionable_items"]
                )
                score += actionable_score * 0.4

            quality_scores.append(score)

        return np.mean(quality_scores) if quality_scores else 0.0

    def _calculate_obstacle_resolution_rate(self, obstacles: List[Dict]) -> float:
        """Calcula la tasa de resolución de obstáculos"""
        if not obstacles:
            return 0.0

        total = len(obstacles)
        resolved = len([o for o in obstacles if o.get("status") == "resolved"])
        in_progress = len([o for o in obstacles if o.get("status") == "in_progress"])

        # Considerar obstáculos en progreso como medio punto
        return (resolved + (in_progress * 0.5)) / total

    def _calculate_hypothesis_validation_rate(self, hypotheses: List[Dict]) -> float:
        """Calcula la tasa de validación de hipótesis"""
        if not hypotheses:
            return 0.0

        total = len(hypotheses)
        validated = len([h for h in hypotheses if h.get("validated")])
        partially_validated = len([h for h in hypotheses if h.get("partially_validated")])

        return (validated + (partially_validated * 0.5)) / total

    def _calculate_target_achievement(
        self,
        actual_state: Dict,
        target_state: Dict

    ) -> float:
        
        """Calcula el progreso hacia el estado objetivo"""
        try:
            actual_metrics = actual_state.get("metrics", {})
            target_metrics = target_state.get("metrics", {})

            if not target_metrics:
                return 0.0

            achievements = []
            for key, target_value in target_metrics.items():
                actual_value = actual_metrics.get(key, 0)
                if target_value != 0:  # Evitar división por cero
                    progress = 1 - abs(target_value - actual_value) / abs(target_value)
                    achievements.append(max(0, min(1, progress)))  # Limitar entre 0 y 1

            return np.mean(achievements) if achievements else 0.0

        except Exception as e:
            self.logger.error(f"Error calculating target achievement: {str(e)}")
            return 0.0

    def _calculate_mental_contrast_score(self, mental_contrast: Dict) -> float:
        """Calcula la puntuación del contraste mental"""
        if not mental_contrast:
            return 0.0

        score = 0
        points = mental_contrast.get("points", 0)
        evaluation_date = mental_contrast.get("evaluation_date")

        # Base score from points (0-10 scale)
        score = points / 10

        # Adjust for recency
        if evaluation_date:
            try:
                eval_date = datetime.fromisoformat(evaluation_date)
                days_since = (datetime.utcnow() - eval_date).days
                if days_since > 30:  # Penalizar evaluaciones antiguas
                    score *= max(0, 1 - ((days_since - 30) / 60))
            except ValueError:
                pass

        return max(0, min(1, score))  # Normalizar entre 0 y 1
    
    async def _evaluate_status(
        self,
        project_data: Dict,
        metrics: KataMetrics
    ) -> KataStatus:
        
        """Evalúa el estado actual del proyecto Kata"""

        try:
            # Determinar estado general
            status = self._determine_project_status(metrics)

            # Identificar necesidades de coaching
            coaching_needs = await self._identify_coaching_needs(
                project_data,
                metrics
            )

            # Identificar obstáculos bloqueantes
            blocking_obstacles = self._identify_blocking_obstacles(
                project_data["obstacles"]
            )

            # Sugerir próximos experimentos
            next_experiments = await self._suggest_next_experiments(
                project_data,
                metrics
            )

            # Identificar factores de riesgo
            risk_factors = self._identify_risk_factors(
                project_data,
                metrics
            )

            return KataStatus(
                status=status,
                coaching_needs=coaching_needs,
                blocking_obstacles=blocking_obstacles,
                next_experiments=next_experiments,
                risk_factors=risk_factors
            )

        except Exception as e:
            self.logger.error(f"Error evaluating status: {str(e)}")
            raise

    def _determine_project_status(self, metrics: KataMetrics) -> str:
        """Determina el estado global del proyecto basado en métricas"""
        # Pesos para diferentes métricas
        weights = {
            'process_adherence': 0.25,
            'learning_quality': 0.20,
            'target_achievement': 0.25,
            'obstacle_resolution_rate': 0.15,
            'hypothesis_validation_rate': 0.15
        }

        # Calcular score ponderado
        weighted_score = (
            metrics.process_adherence * weights['process_adherence'] +
            metrics.learning_quality * weights['learning_quality'] +
            metrics.target_achievement * weights['target_achievement'] +
            metrics.obstacle_resolution_rate * weights['obstacle_resolution_rate'] +
            metrics.hypothesis_validation_rate * weights['hypothesis_validation_rate']
        )

        # Determinar estado basado en score
        if weighted_score >= 0.75:
            return "on_track"
        elif weighted_score >= 0.5:
            return "needs_adjustment"
        else:
            return "at_risk"

    async def _identify_coaching_needs(
        self,
        project_data: Dict,
        metrics: KataMetrics
    ) -> List[str]:
        """Identifica áreas que necesitan coaching"""
        coaching_needs = []

        # 1. Verificar adherencia al proceso
        if metrics.process_adherence < 0.6:
            coaching_needs.append("Reforzar comprensión del proceso Kata")

        # 2. Analizar calidad de experimentos
        if metrics.experiment_cycle_time > 14:  # Ciclos mayores a 2 semanas
            coaching_needs.append("Mejorar diseño de experimentos para ciclos más cortos")

        # 3. Evaluar aprendizajes
        if metrics.learning_quality < 0.5:
            coaching_needs.append("Profundizar en la documentación de aprendizajes")

        # 4. Verificar hipótesis
        if metrics.hypothesis_validation_rate < 0.4:
            coaching_needs.append("Mejorar formulación de hipótesis")

        # 5. Analizar obstáculos
        if len(project_data["obstacles"]) > 0 and metrics.obstacle_resolution_rate < 0.3:
            coaching_needs.append("Reforzar estrategias de resolución de obstáculos")

        return coaching_needs

    def _identify_blocking_obstacles(self, obstacles: List[Dict]) -> List[Dict]:
        """Identifica obstáculos que están bloqueando el progreso"""
        blocking = []
        for obstacle in obstacles:
            if obstacle.get("status") != "resolved":
                dependencies = len(obstacle.get("dependencies", []))
                impact = obstacle.get("impact_level", 0)
                
                # Criterios para considerar un obstáculo como bloqueante
                if any([
                    impact >= 4,  # Alto impacto
                    dependencies >= 2,  # Múltiples dependencias
                    obstacle.get("blocks_target_state", False),  # Bloquea estado objetivo
                    obstacle.get("priority", "") == "high"  # Alta prioridad
                ]):
                    blocking.append({
                        "id": obstacle.get("id"),
                        "description": obstacle.get("description"),
                        "impact": impact,
                        "dependencies": dependencies,
                        "priority": obstacle.get("priority")
                    })

        return sorted(blocking, key=lambda x: x["impact"], reverse=True)

    async def _suggest_next_experiments(
        self,
        project_data: Dict,
        metrics: KataMetrics
    ) -> List[Dict]:
        """Sugiere próximos experimentos basados en el estado actual"""
        try:
            # Preparar contexto para el LLM
            context = {
                "current_state": project_data["actual_state"],
                "target_state": project_data["target_state"],
                "active_obstacles": [o for o in project_data["obstacles"] 
                                  if o.get("status") != "resolved"],
                "recent_experiments": project_data["experiments"][-3:],
                "metrics": metrics.dict()
            }

            # Solicitar sugerencias al LLM
            response = await self.orchestrator.process_query(
                query="Suggest next experiments for this Kata project",
                response_type=ResponseType.SUGGESTION,
                metadata={"context": context}
            )

            # Procesar respuesta
            suggestions = self._process_experiment_suggestions(response)
            return suggestions

        except Exception as e:
            self.logger.error(f"Error suggesting experiments: {str(e)}")
            return []

    def _identify_risk_factors(
        self,
        project_data: Dict,
        metrics: KataMetrics
    ) -> List[str]:
        """Identifica factores de riesgo en el proyecto"""
        risk_factors = []

        # 1. Riesgos de proceso
        if metrics.process_adherence < 0.5:
            risk_factors.append("Baja adherencia al proceso Kata")

        # 2. Riesgos de experimentación
        if metrics.experiment_cycle_time > 21:  # Ciclos mayores a 3 semanas
            risk_factors.append("Ciclos de experimentación demasiado largos")

        # 3. Riesgos de aprendizaje
        if metrics.learning_quality < 0.4:
            risk_factors.append("Calidad insuficiente en documentación de aprendizajes")

        # 4. Riesgos de obstáculos
        blocking_count = len([o for o in project_data["obstacles"] 
                            if o.get("status") == "blocked"])
        if blocking_count > 2:
            risk_factors.append(f"Múltiples obstáculos bloqueados ({blocking_count})")

        # 5. Riesgos de objetivo
        if metrics.target_achievement < 0.3:
            risk_factors.append("Progreso insuficiente hacia estado objetivo")

        # 6. Riesgos de hipótesis
        if metrics.hypothesis_validation_rate < 0.3:
            risk_factors.append("Baja tasa de validación de hipótesis")

        return risk_factors

    async def _generate_insights(
        self,
        project_data: Dict,
        metrics: KataMetrics
    ) -> List[str]:
        
        """Genera insights basados en datos y métricas del proyecto"""

        try:
            # Preparar contexto
            context = self._prepare_insight_context(project_data, metrics)

            # Solicitar insights al LLM
            response = await self.orchestrator.process_query(
                query=self._generate_insight_prompt(context),
                response_type=ResponseType.ANALYSIS,
                metadata={"context": context}
            )

            # Validar y procesar insights
            insights = self._process_llm_insights(response)
            return insights

        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return []

    def _prepare_insight_context(
        self,
        project_data: Dict,
        metrics: KataMetrics
    ) -> Dict:
        
        """Prepara el contexto para generación de insights"""

        return {
            "challenge": {
                "description": project_data["challenge"].get("description"),
                "target": project_data["target_state"].get("description"),
                "current": project_data["actual_state"].get("description")
            },
            "progress": {
                "metrics": metrics.dict(),
                "experiments": len(project_data["experiments"]),
                "learnings": len(project_data["learnings"]),
                "resolved_obstacles": sum(1 for o in project_data["obstacles"] 
                                       if o.get("status") == "resolved")
            },
            "trends": {
                "experiment_success": self._calculate_experiment_trend(
                    project_data["experiments"]
                ),
                "learning_quality": self._calculate_learning_trend(
                    project_data["learnings"]
                )
            }
        }

    def _generate_insight_prompt(self, context: Dict) -> str:

        """Genera el prompt para solicitar insights"""

        return f"""Analiza el siguiente proyecto Kata y genera insights significativos:

        Challenge: {context['challenge']['description']}
        Estado Objetivo: {context['challenge']['target']}
        Estado Actual: {context['challenge']['current']}

        Métricas actuales:
        {json.dumps(context['progress'], indent=2)}

        Tendencias:
        {json.dumps(context['trends'], indent=2)}

        Genera 3-5 insights relevantes que ayuden a mejorar el proceso Kata."""

    def _process_llm_insights(self, response: LLMResponse) -> List[str]:

        """Procesa y valida los insights generados por el LLM"""

        insights = []
        
        # Separar por líneas y filtrar líneas vacías
        raw_insights = [line.strip() for line in response.content.split('\n') 
                       if line.strip()]

        for insight in raw_insights:
            # Remover numeración y caracteres especiales
            cleaned = re.sub(r'^\d+[\.\)]\s*', '', insight)
            cleaned = cleaned.strip('- ').strip()
            
            # Validar longitud y contenido
            if len(cleaned) > 20 and not any(existing in cleaned 
                                           for existing in insights):
                insights.append(cleaned)

        return insights[:5]  # Limitar a 5 insights máximo

    async def _generate_recommendations(
        self,
        project_data: Dict,
        metrics: KataMetrics,
        status: KataStatus
    ) -> List[Dict[str, Any]]:
        
        """Genera recomendaciones específicas para el proyecto"""

        try:
            # Preparar contexto
            context = {
                "metrics": metrics.dict(),
                "status": status.dict(),
                "project_state": {
                    "challenge": project_data["challenge"].get("description"),
                    "blocking_obstacles": [o for o in project_data["obstacles"] 
                                        if o.get("status") == "blocked"],
                    "recent_experiments": project_data["experiments"][-3:],
                    "recent_learnings": project_data["learnings"][-3:]
                }
            }

            # Solicitar recomendaciones al LLM
            response = await self.orchestrator.process_query(
                query=self._generate_recommendation_prompt(context),
                response_type=ResponseType.SUGGESTION,
                metadata={"context": context}
            )

            # Procesar y estructurar recomendaciones
            recommendations = self._process_llm_recommendations(response)
            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _generate_recommendation_prompt(self, context: Dict) -> str:

        """Genera el prompt para solicitar recomendaciones"""

        return f"""Basado en el siguiente estado del proyecto Kata:

        Estado actual: {context['status']['status']}
        Métricas clave: {json.dumps(context['metrics'], indent=2)}
        Obstáculos bloqueantes: {len(context['project_state']['blocking_obstacles'])}

        Genera 3-5 recomendaciones específicas y accionables para mejorar el proceso Kata.
        Para cada recomendación, incluye:
        1. Acción específica
        2. Prioridad (alta/media/baja)
        3. Impacto esperado
        4. Tiempo estimado de implementación"""

    def _process_llm_recommendations(
        self,
        response: LLMResponse
    ) -> List[Dict[str, Any]]:
        
        """Procesa y estructura las recomendaciones generadas por el LLM"""

        recommendations = []
        
        # Separar por líneas y filtrar líneas vacías
        raw_recommendations = [line.strip() for line in response.content.split('\n') 
                             if line.strip()]

        current_rec = {}
        for line in raw_recommendations:
            if line.startswith('Acción:'):
                if current_rec:
                    recommendations.append(current_rec)
                current_rec = {'action': line[7:].strip()}
            elif line.startswith('Prioridad:'):
                current_rec['priority'] = line[10:].strip().lower()
            elif line.startswith('Impacto:'):
                current_rec['impact'] = line[8:].strip()
            elif line.startswith('Tiempo:'):
                current_rec['estimated_time'] = line[7:].strip()

        if current_rec:
            recommendations.append(current_rec)

        return recommendations
    
    def _calculate_experiment_trend(self, experiments: List[Dict]) -> Dict[str, Any]:

        """Calcula tendencias en experimentos"""
        
        if not experiments:
            return {"trend": "no_data", "success_rate": 0}

        # Ordenar experimentos por fecha
        sorted_experiments = sorted(
            experiments,
            key=lambda x: datetime.fromisoformat(x.get("start_date", "2000-01-01"))
        )

        # Calcular tasas de éxito por periodo
        periods = []
        success_rates = []
        window_size = min(3, len(sorted_experiments))  # Ventana móvil de 3 o menos

        for i in range(len(sorted_experiments) - window_size + 1):
            window = sorted_experiments[i:i + window_size]
            successful = len([e for e in window if e.get("results", {}).get("success", False)])
            success_rate = successful / window_size
            periods.append(i)
            success_rates.append(success_rate)

        # Determinar tendencia
        if len(success_rates) >= 2:
            recent_rate = success_rates[-1]
            previous_rate = success_rates[0]
            if recent_rate > previous_rate + 0.1:
                trend = "improving"
            elif recent_rate < previous_rate - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "trend": trend,
            "success_rate": success_rates[-1] if success_rates else 0,
            "data_points": list(zip(periods, success_rates))
        }

    def _calculate_learning_trend(self, learnings: List[Dict]) -> Dict[str, Any]:

        """Calcula tendencias en la calidad de aprendizajes"""

        if not learnings:
            return {"trend": "no_data", "quality_score": 0}

        # Ordenar aprendizajes por fecha
        sorted_learnings = sorted(
            learnings,
            key=lambda x: datetime.fromisoformat(x.get("learning_date", "2000-01-01"))
        )

        # Calcular calidad por periodo
        quality_scores = []
        periods = []
        window_size = min(3, len(sorted_learnings))

        for i in range(len(sorted_learnings) - window_size + 1):
            window = sorted_learnings[i:i + window_size]
            quality = np.mean([
                self._evaluate_single_learning(learning)
                for learning in window
            ])
            periods.append(i)
            quality_scores.append(quality)

        # Determinar tendencia
        if len(quality_scores) >= 2:
            recent_quality = quality_scores[-1]
            previous_quality = quality_scores[0]
            if recent_quality > previous_quality + 0.1:
                trend = "improving"
            elif recent_quality < previous_quality - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "trend": trend,
            "quality_score": quality_scores[-1] if quality_scores else 0,
            "data_points": list(zip(periods, quality_scores))
        }

    def _evaluate_single_learning(self, learning: Dict) -> float:

        """Evalúa la calidad de un único aprendizaje"""

        score = 0
        max_score = 5

        # 1. Completitud de descripción
        description = learning.get("description", "")
        if len(description) > 200:
            score += 1
        elif len(description) > 100:
            score += 0.5

        # 2. Presencia de evidencia
        if learning.get("evidence"):
            score += 1

        # 3. Items accionables
        if learning.get("actionable_items"):
            score += 1

        # 4. Vinculación con hipótesis
        if learning.get("related_hypothesis"):
            score += 1

        # 5. Método de validación
        if learning.get("validation_method"):
            score += 1

        return score / max_score

    async def _calculate_semantic_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        
        """Calcula la similitud semántica entre dos textos usando el vector store"""
        
        try:
            # Convertir textos a vectores usando el vector store
            vector1 = await self.vector_store.vectorizer.vectorize([text1])
            vector2 = await self.vector_store.vectorizer.vectorize([text2])

            # Calcular similitud coseno
            similarity = np.dot(vector1[0], vector2[0]) / (
                np.linalg.norm(vector1[0]) * np.linalg.norm(vector2[0])
            )

            return float(similarity)

        except Exception as e:
            self.logger.error(f"Error calculating semantic similarity: {str(e)}")
            return 0.0

    def _evaluate_actionability(self, action_items: List[str]) -> float:

        """Evalúa la accionabilidad de los items propuestos"""
        
        if not action_items:
            return 0.0

        score = 0
        for item in action_items:
            item_score = 0
            
            # 1. Especificidad
            if len(item) > 20:  # Suficientemente detallado
                item_score += 0.3
                
            # 2. Verbos de acción
            action_verbs = ["implementar", "crear", "desarrollar", "medir", "evaluar", 
                          "analizar", "modificar", "actualizar", "diseñar"]
            if any(verb in item.lower() for verb in action_verbs):
                item_score += 0.4
                
            # 3. Medibilidad
            if any(metric in item.lower() for metric in ["porcentaje", "número", "cantidad", 
                                                       "tasa", "tiempo", "frecuencia"]):
                item_score += 0.3
                
            score += item_score

        return score / len(action_items)

    def _format_date(self, date_str: str) -> str:

        """Formatea una fecha para presentación"""
        
        try:
            date = datetime.fromisoformat(date_str)
            return date.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return "Fecha no válida"

    def _calculate_time_difference(
        self,
        start_date: str,
        end_date: str
    ) -> Optional[int]:
        
        """Calcula la diferencia en días entre dos fechas"""
        
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            return (end - start).days
        except (ValueError, TypeError):
            return None

    def _is_valid_experiment(self, experiment: Dict) -> bool:

        """Valida si un experimento cumple con los criterios mínimos"""
        required_fields = [
            "hypothesis",
            "methodology",
            "start_date",
            "end_date",
            "results"
        ]
        return all(experiment.get(field) for field in required_fields)


    def _is_valid_learning(self, learning: Dict) -> bool:

        """Valida si un aprendizaje cumple con los criterios mínimos"""
        
        required_fields = [
            "description",
            "learning_date",
            "actionable_items"
        ]
        return all(learning.get(field) for field in required_fields)