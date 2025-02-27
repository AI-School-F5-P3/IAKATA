from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field
import numpy as np
import json
import re

from app.llm.types import ResponseType, LLMResponse
from app.orchestrator.orchestrator import RAGOrchestrator
from app.vectorstore.vector_store import VectorStore

# Modelos para análisis
class KataMetrics(BaseModel):
    """Métricas clave para evaluación de proyectos Lean Kata"""
    process_adherence: float = Field(..., description="Adherencia al proceso Kata (0-1)")
    experiment_cycle_time: float = Field(..., description="Tiempo medio del ciclo PDCA en días")
    learning_quality: float = Field(..., description="Calidad de aprendizajes (0-1)")
    obstacle_resolution_rate: float = Field(..., description="Tasa de resolución de obstáculos")
    hypothesis_validation_rate: float = Field(..., description="Tasa de validación de hipótesis")
    target_achievement: float = Field(..., description="Progreso hacia el estado objetivo")
    
    @property
    def overall_score(self) -> float:
        """Calcula el puntaje general basado en todas las métricas"""
        weights = {
            'process_adherence': 0.2,
            'experiment_cycle_time': 0.15,
            'learning_quality': 0.2,
            'obstacle_resolution_rate': 0.15,
            'hypothesis_validation_rate': 0.15,
            'target_achievement': 0.15
        }
        
        # Normalizar experiment_cycle_time (valor más bajo es mejor)
        normalized_cycle_time = max(0, min(1, 1 - (self.experiment_cycle_time / 30)))
        
        return (
            self.process_adherence * weights['process_adherence'] +
            normalized_cycle_time * weights['experiment_cycle_time'] +
            self.learning_quality * weights['learning_quality'] +
            self.obstacle_resolution_rate * weights['obstacle_resolution_rate'] +
            self.hypothesis_validation_rate * weights['hypothesis_validation_rate'] +
            self.target_achievement * weights['target_achievement']
        )
    
    def to_display_dict(self) -> Dict:
        """Convierte las métricas a un formato amigable para visualización"""
        return {
            "adherencia_proceso": f"{self.process_adherence * 100:.1f}%",
            "tiempo_ciclo_experimentos": f"{self.experiment_cycle_time:.1f} días",
            "calidad_aprendizajes": f"{self.learning_quality * 100:.1f}%",
            "tasa_resolucion_obstaculos": f"{self.obstacle_resolution_rate * 100:.1f}%",
            "tasa_validacion_hipotesis": f"{self.hypothesis_validation_rate * 100:.1f}%",
            "progreso_objetivo": f"{self.target_achievement * 100:.1f}%",
            "puntaje_general": f"{self.overall_score * 100:.1f}%"
        }

class ProjectInsight(BaseModel):
    """Insight extraído del análisis de un proyecto"""
    type: str = Field(..., description="Tipo de insight (strength, improvement, risk)")
    description: str = Field(..., description="Descripción del insight")
    related_metric: Optional[str] = Field(None, description="Métrica relacionada con el insight")
    importance: int = Field(1, description="Importancia del insight (1-3)")

class KataRecommendation(BaseModel):
    """Recomendación para mejorar un proyecto Kata"""
    action: str = Field(..., description="Acción recomendada")
    priority: str = Field(..., description="Prioridad (alta, media, baja)")
    impact: str = Field(..., description="Impacto esperado")
    estimated_time: str = Field(..., description="Tiempo estimado de implementación")
    
class ProjectStatus(BaseModel):
    """Estado actual de un proyecto Kata"""
    status: str = Field(..., description="Estado global (on_track, needs_adjustment, at_risk)")
    coaching_needs: List[str] = Field(default_factory=list, description="Áreas que necesitan coaching")
    blocking_obstacles: List[Dict] = Field(default_factory=list, description="Obstáculos bloqueantes")
    risk_factors: List[str] = Field(default_factory=list, description="Factores de riesgo identificados")
    
class ProjectAnalysis(BaseModel):
    """Análisis completo de un proyecto Kata"""
    project_id: str
    project_name: str
    metrics: KataMetrics
    status: ProjectStatus
    insights: List[ProjectInsight]
    recommendations: List[KataRecommendation]
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    previous_score: Optional[float] = None
    
    def trend(self) -> str:
        """Determina la tendencia del proyecto comparando con análisis anterior"""
        if self.previous_score is None:
            return "neutral"
        
        diff = self.metrics.overall_score - self.previous_score
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"

class KataAnalyzer:
    """Analizador de proyectos Lean Kata"""
    
    def __init__(
        self,
        orchestrator: RAGOrchestrator,
        vector_store: VectorStore,
        db_connector,  # Conexión a la base de datos
        cache_ttl: int = 3600  # Tiempo de vida de la caché en segundos
    ):
        self.orchestrator = orchestrator
        self.vector_store = vector_store
        self.db = db_connector
        self.cache_ttl = cache_ttl
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._last_update = {}
    
    async def analyze_project(self, project_id: str, refresh: bool = False) -> ProjectAnalysis:
        """
        Analiza un proyecto Lean Kata y genera métricas, insights y recomendaciones
        
        Args:
            project_id: ID del proyecto a analizar
            refresh: Si es True, fuerza recálculo incluso si hay caché
            
        Returns:
            ProjectAnalysis con los resultados del análisis
        """
        try:
            # Verificar caché
            if not refresh and self._is_cache_valid(project_id):
                self.logger.info(f"Retornando análisis en caché para proyecto {project_id}")
                return self._cache[project_id]

            # Obtener datos del proyecto
            project_data = await self._fetch_project_data(project_id)
            
            # Obtener análisis anterior para comparación
            previous_analysis = await self._get_previous_analysis(project_id)
            previous_score = previous_analysis.metrics.overall_score if previous_analysis else None
            
            # Calcular métricas actuales
            metrics = await self._calculate_metrics(project_data)
            
            # Evaluar estado actual
            status = await self._evaluate_status(project_data, metrics)
            
            # Generar insights
            insights = await self._generate_insights(project_data, metrics, previous_analysis)
            
            # Generar recomendaciones
            recommendations = await self._generate_recommendations(
                project_data, 
                metrics, 
                status,
                insights
            )

            # Crear análisis completo
            analysis = ProjectAnalysis(
                project_id=project_id,
                project_name=project_data.get("challenge", {}).get("name", "Proyecto sin nombre"),
                metrics=metrics,
                status=status,
                insights=insights,
                recommendations=recommendations,
                previous_score=previous_score
            )

            # Guardar análisis en caché y en base de datos
            self._update_cache(project_id, analysis)
            await self._save_analysis(analysis)
            
            self.logger.info(f"Análisis completado para proyecto {project_id}")
            return analysis

        except Exception as e:
            self.logger.error(f"Error analizando proyecto {project_id}: {str(e)}")
            raise
    
    async def get_project_trend(self, project_id: str, time_range: int = 30) -> Dict:
        """
        Obtiene la tendencia de un proyecto a lo largo del tiempo
        
        Args:
            project_id: ID del proyecto
            time_range: Rango de tiempo en días para análisis
            
        Returns:
            Diccionario con datos de tendencia
        """
        try:
            # Obtener análisis históricos
            historical_data = await self.db.fetch_analyses(
                project_id=project_id,
                from_date=datetime.utcnow() - timedelta(days=time_range)
            )
            
            if not historical_data:
                return {"trend": "insufficient_data", "data_points": []}
            
            # Preparar datos para visualización
            trend_data = []
            for analysis in historical_data:
                trend_data.append({
                    "date": analysis["analyzed_at"].strftime("%Y-%m-%d"),
                    "overall_score": analysis["metrics"]["overall_score"],
                    "adherence": analysis["metrics"]["process_adherence"],
                    "target_progress": analysis["metrics"]["target_achievement"]
                })
            
            # Calcular tendencia
            if len(trend_data) >= 2:
                first_score = trend_data[0]["overall_score"]
                last_score = trend_data[-1]["overall_score"]
                diff = last_score - first_score
                
                if diff > 0.1:
                    trend = "strong_improvement"
                elif diff > 0.05:
                    trend = "improvement"
                elif diff < -0.1:
                    trend = "strong_decline"
                elif diff < -0.05:
                    trend = "decline"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            return {
                "trend": trend,
                "data_points": trend_data
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo tendencia del proyecto {project_id}: {str(e)}")
            return {"trend": "error", "data_points": [], "error": str(e)}
            
    async def get_organization_kpis(self) -> Dict:
        """
        Obtiene KPIs a nivel organizacional basados en todos los proyectos
        
        Returns:
            Diccionario con KPIs organizacionales
        """
        try:
            # Obtener datos de todos los proyectos activos
            all_projects = await self.db.fetch_active_projects()
            
            if not all_projects:
                return {"status": "no_data", "message": "No hay proyectos activos"}
            
            # Analizar todos los proyectos
            all_analyses = []
            for project in all_projects:
                try:
                    analysis = await self.analyze_project(project["id"])
                    all_analyses.append(analysis)
                except Exception as e:
                    self.logger.error(f"Error analizando proyecto {project['id']}: {str(e)}")
            
            if not all_analyses:
                return {"status": "error", "message": "No se pudieron analizar los proyectos"}
            
            # Calcular KPIs organizacionales
            kpis = {
                "total_projects": len(all_projects),
                "analyzed_projects": len(all_analyses),
                "average_metrics": {
                    "overall_score": np.mean([a.metrics.overall_score for a in all_analyses]),
                    "process_adherence": np.mean([a.metrics.process_adherence for a in all_analyses]),
                    "learning_quality": np.mean([a.metrics.learning_quality for a in all_analyses]),
                    "target_achievement": np.mean([a.metrics.target_achievement for a in all_analyses])
                },
                "project_status": {
                    "on_track": sum(1 for a in all_analyses if a.status.status == "on_track"),
                    "needs_adjustment": sum(1 for a in all_analyses if a.status.status == "needs_adjustment"),
                    "at_risk": sum(1 for a in all_analyses if a.status.status == "at_risk")
                },
                "common_coaching_needs": self._identify_common_coaching_needs(all_analyses),
                "top_performing_projects": self._get_top_performing_projects(all_analyses, limit=3),
                "most_improved_projects": await self._get_most_improved_projects(limit=3)
            }
            
            return kpis
            
        except Exception as e:
            self.logger.error(f"Error obteniendo KPIs organizacionales: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _fetch_project_data(self, project_id: str) -> Dict:
        """
        Obtiene los datos completos de un proyecto desde la base de datos
        
        Adapta esta función según tu modelo de datos actual
        """
        try:
            # Obtener proceso
            process = await self.db.fetch_one("processes", {"id": project_id})
            if not process:
                raise ValueError(f"Proceso no encontrado: {project_id}")
            
            # Obtener tribu
            tribe = await self.db.fetch_one("tribes", {"process_id": process["id"]})
            
            # Obtener reto
            challenge = await self.db.fetch_one("challenges", {"tribe_id": tribe["id"]})
            
            # Obtener estados
            actual_state = await self.db.fetch_one("actual_states", {"challenge_id": challenge["id"]})
            target_state = await self.db.fetch_one("target_states", {"challenge_id": challenge["id"]})
            
            # Obtener elementos de experimentación
            obstacles = await self.db.fetch_all("obstacles", {"target_state_id": target_state["id"]})
            
            obstacle_ids = [o["id"] for o in obstacles]
            hypotheses = await self.db.fetch_all("hypotheses", {"obstacle_id": {"$in": obstacle_ids}})
            
            hypothesis_ids = [h["id"] for h in hypotheses]
            experiments = await self.db.fetch_all("experiments", {"hypothesis_id": {"$in": hypothesis_ids}})
            
            # Obtener resultados y aprendizajes
            experiment_ids = [e["id"] for e in experiments]
            results = await self.db.fetch_all("results", {"experiment_id": {"$in": experiment_ids}})
            
            result_ids = [r["id"] for r in results]
            learnings = await self.db.fetch_all("learnings", {"results_id": {"$in": result_ids}})
            
            # Obtener contraste mental
            mental_contrast = await self.db.fetch_one("mental_contrasts", 
                                                    {"target_state_id": target_state["id"]})

            return {
                "process": process,
                "tribe": tribe,
                "challenge": challenge,
                "actual_state": actual_state,
                "target_state": target_state,
                "obstacles": obstacles,
                "hypotheses": hypotheses,
                "experiments": experiments,
                "results": results,
                "learnings": learnings,
                "mental_contrast": mental_contrast
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo datos del proyecto {project_id}: {str(e)}")
            raise
    
    async def _calculate_metrics(self, project_data: Dict) -> KataMetrics:
        """Calcula métricas clave para el proyecto Kata"""
        
        # Adherencia al proceso
        process_adherence = self._calculate_process_adherence(
            project_data["experiments"],
            project_data["learnings"]
        )
        
        # Tiempo de ciclo de experimentos
        cycle_time = self._calculate_experiment_cycle_time(
            project_data["experiments"]
        )
        
        # Calidad de aprendizajes
        learning_quality = self._calculate_learning_quality(
            project_data["learnings"]
        )
        
        # Tasa de resolución de obstáculos
        obstacle_rate = self._calculate_obstacle_resolution_rate(
            project_data["obstacles"]
        )
        
        # Tasa de validación de hipótesis
        hypothesis_rate = self._calculate_hypothesis_validation_rate(
            project_data["hypotheses"],
            project_data["experiments"]
        )
        
        # Progreso hacia objetivo
        target_achievement = self._calculate_target_achievement(
            project_data["actual_state"],
            project_data["target_state"]
        )
        
        return KataMetrics(
            process_adherence=process_adherence,
            experiment_cycle_time=cycle_time,
            learning_quality=learning_quality,
            obstacle_resolution_rate=obstacle_rate,
            hypothesis_validation_rate=hypothesis_rate,
            target_achievement=target_achievement
        )
    
    def _calculate_process_adherence(self, experiments: List[Dict], learnings: List[Dict]) -> float:
        """
        Calcula la adherencia al proceso Kata basado en completitud y calidad
        de experimentos y aprendizajes
        """
        if not experiments:
            return 0.0
        
        experiment_scores = []
        for exp in experiments:
            score = 0
            # Plan
            if exp.get("methodology") and len(str(exp.get("methodology", ""))) > 20:
                score += 0.25
            # Do
            if exp.get("execution_details") and exp.get("start_date"):
                score += 0.25
            # Check
            if exp.get("results_obtained") or exp.get("results_id"):
                score += 0.25
            # Act
            if exp.get("next_steps") or exp.get("conclusions"):
                score += 0.25
            experiment_scores.append(score)
        
        learning_scores = []
        for learning in learnings:
            score = 0
            if learning.get("description") and len(str(learning.get("description", ""))) > 30:
                score += 0.5
            if learning.get("actionable_items"):
                score += 0.5
            learning_scores.append(score)
        
        exp_score = np.mean(experiment_scores) if experiment_scores else 0
        learn_score = np.mean(learning_scores) if learning_scores else 0
        
        # 70% experimentos, 30% aprendizajes
        return (exp_score * 0.7) + (learn_score * 0.3)
    
    def _calculate_experiment_cycle_time(self, experiments: List[Dict]) -> float:
        """Calcula el tiempo promedio del ciclo de experimentos en días"""
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
                    # Solo considerar ciclos válidos (1-60 días)
                    if 1 <= duration <= 60:
                        cycle_times.append(duration)
                except (ValueError, TypeError):
                    continue
        
        return np.mean(cycle_times) if cycle_times else 0.0
    
    def _calculate_learning_quality(self, learnings: List[Dict]) -> float:
        """Evalúa la calidad de los aprendizajes documentados"""
        if not learnings:
            return 0.0
        
        quality_scores = []
        for learning in learnings:
            score = 0
            
            # Evaluar descripción
            description = str(learning.get("description", ""))
            if len(description) > 100:
                score += 0.4
            elif len(description) > 50:
                score += 0.2
            
            # Evaluar accionabilidad
            if learning.get("actionable_items"):
                items = learning["actionable_items"]
                if isinstance(items, list) and len(items) > 0:
                    score += 0.3
                elif isinstance(items, str) and len(items) > 20:
                    score += 0.2
            
            # Evaluar vinculación a resultados
            if learning.get("results_id"):
                score += 0.3
            
            quality_scores.append(score)
        
        return np.mean(quality_scores) if quality_scores else 0.0
    
    def _calculate_obstacle_resolution_rate(self, obstacles: List[Dict]) -> float:
        """Calcula la tasa de resolución de obstáculos"""
        if not obstacles:
            return 0.0
        
        total = len(obstacles)
        resolved = len([o for o in obstacles if o.get("status") == "resolved"])
        in_progress = len([o for o in obstacles if o.get("status") == "in_progress"])
        
        # Obstáculos en progreso cuentan como mitad
        return (resolved + (in_progress * 0.5)) / total
    
    def _calculate_hypothesis_validation_rate(self, hypotheses: List[Dict], experiments: List[Dict]) -> float:
        """Calcula la tasa de validación de hipótesis"""
        if not hypotheses:
            return 0.0
        
        # Mapear hipótesis a experimentos
        hypothesis_experiments = {}
        for exp in experiments:
            hyp_id = exp.get("hypothesis_id")
            if hyp_id:
                if hyp_id not in hypothesis_experiments:
                    hypothesis_experiments[hyp_id] = []
                hypothesis_experiments[hyp_id].append(exp)
        
        # Evaluar validación de cada hipótesis
        validated = 0
        partially_validated = 0
        
        for hyp in hypotheses:
            hyp_id = hyp.get("id")
            exps = hypothesis_experiments.get(hyp_id, [])
            
            # Verificar si hay experimentos con resultados
            has_results = any(e.get("results_id") for e in exps)
            
            # Verificar estado de validación explícito
            if hyp.get("validated") is True:
                validated += 1
            elif hyp.get("partially_validated") is True or has_results:
                partially_validated += 1
        
        total = len(hypotheses)
        return (validated + (partially_validated * 0.5)) / total
    
    def _calculate_target_achievement(self, actual_state: Dict, target_state: Dict) -> float:
        """Calcula el progreso hacia el estado objetivo"""
        if not actual_state or not target_state:
            return 0.0
        
        try:
            # Intentar extraer métricas de estado actual y objetivo
            current_metrics = self._extract_metrics(actual_state)
            target_metrics = self._extract_metrics(target_state)
            
            if not current_metrics or not target_metrics:
                return self._estimate_progress_from_description(
                    actual_state.get("description", ""), 
                    target_state.get("description", "")
                )
            
            # Calcular progreso para cada métrica
            progresses = []
            for key, target_value in target_metrics.items():
                if key in current_metrics and target_value != 0:
                    current_value = current_metrics[key]
                    if isinstance(target_value, (int, float)) and isinstance(current_value, (int, float)):
                        # Si el valor objetivo es mayor que el inicial
                        if target_value > current_metrics.get(f"initial_{key}", 0):
                            progress = min(1, max(0, current_value / target_value))
                        else:  # Si el objetivo es reducir
                            initial = current_metrics.get(f"initial_{key}", current_value * 2)
                            progress = min(1, max(0, (initial - current_value) / (initial - target_value)))
                        progresses.append(progress)
            
            return np.mean(progresses) if progresses else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculando progreso hacia objetivo: {str(e)}")
            return 0.0
    
    def _extract_metrics(self, state: Dict) -> Dict[str, float]:
        """Extrae métricas numéricas de la descripción del estado"""
        if not state:
            return {}
        
        metrics = {}
        
        # Primero intentar usar campo específico de métricas si existe
        if state.get("metrics") and isinstance(state["metrics"], dict):
            return state["metrics"]
        
        # Si no hay campo específico, intentar extraer de la descripción
        description = state.get("description", "")
        
        # Buscar patrones como "Métrica: 75%" o "KPI: 120 días"
        pattern = r'(\w+[\s\w]*?):\s*(\d+\.?\d*)\s*(%|días|horas|unidades)?'
        matches = re.findall(pattern, description)
        
        for match in matches:
            metric_name = match[0].strip().lower().replace(" ", "_")
            value = float(match[1])
            unit = match[2] if len(match) > 2 else ""
            
            if unit == "%":
                value /= 100  # Normalizar porcentajes
                
            metrics[metric_name] = value
        
        return metrics
    
    def _estimate_progress_from_description(self, actual_desc: str, target_desc: str) -> float:
        """Estima el progreso cuando no hay métricas específicas"""
        # Esta es una estimación simple basada en palabras clave
        progress_indicators = ["completado", "finalizado", "logrado", "alcanzado"]
        partial_indicators = ["avanzando", "progresando", "mejorando", "en proceso"]
        
        actual_lower = actual_desc.lower()
        
        if any(indicator in actual_lower for indicator in progress_indicators):
            return 0.9
        elif any(indicator in actual_lower for indicator in partial_indicators):
            return 0.5
        else:
            return 0.1
    
    async def _evaluate_status(self, project_data: Dict, metrics: KataMetrics) -> ProjectStatus:
        """Evalúa el estado actual del proyecto Kata"""
        
        # Determinar estado general basado en métricas
        overall_score = metrics.overall_score
        if overall_score >= 0.7:
            status = "on_track"
        elif overall_score >= 0.4:
            status = "needs_adjustment"
        else:
            status = "at_risk"
        
        # Identificar necesidades de coaching
        coaching_needs = self._identify_coaching_needs(project_data, metrics)
        
        # Identificar obstáculos bloqueantes
        blocking_obstacles = self._identify_blocking_obstacles(project_data["obstacles"])
        
        # Identificar factores de riesgo
        risk_factors = self._identify_risk_factors(project_data, metrics)
        
        return ProjectStatus(
            status=status,
            coaching_needs=coaching_needs,
            blocking_obstacles=blocking_obstacles,
            risk_factors=risk_factors
        )
    
    def _identify_coaching_needs(self, project_data: Dict, metrics: KataMetrics) -> List[str]:
        """Identifica áreas que necesitan coaching basado en métricas y datos del proyecto"""
        coaching_needs = []
        
        # Verificar adherencia al proceso
        if metrics.process_adherence < 0.6:
            coaching_needs.append("Reforzar comprensión del proceso Kata")
        
        # Analizar ciclo de experimentos
        if metrics.experiment_cycle_time > 14:  # Si los ciclos son mayores a 2 semanas
            coaching_needs.append("Mejorar diseño de experimentos para ciclos más cortos")
        
        # Evaluar calidad de aprendizajes
        if metrics.learning_quality < 0.5:
            coaching_needs.append("Mejorar calidad y accionabilidad de aprendizajes")
        
        # Analizar resolución de obstáculos
        if metrics.obstacle_resolution_rate < 0.3:
            coaching_needs.append("Estrategias efectivas para abordar obstáculos")
        
        # Verificar progreso al objetivo
        if metrics.target_achievement < 0.3 and project_data.get("target_state"):
            coaching_needs.append("Alineación de experimentos con el estado objetivo")
        
        # Verificar actividad reciente
        recent_activity = self._check_recent_activity(project_data)
        if not recent_activity:
            coaching_needs.append("Retomar ritmo de trabajo activo en el proyecto")
        
        return coaching_needs
    
    def _check_recent_activity(self, project_data: Dict) -> bool:
        """Verifica si hay actividad reciente en el proyecto (últimos 14 días)"""
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        
        # Buscar fechas recientes en experimentos
        for exp in project_data.get("experiments", []):
            for date_field in ["start_date", "end_date", "updated_at"]:
                if exp.get(date_field):
                    try:
                        date = datetime.fromisoformat(exp[date_field])
                        if date > two_weeks_ago:
                            return True
                    except (ValueError, TypeError):
                        continue
        
        # Buscar fechas recientes en aprendizajes
        for learning in project_data.get("learnings", []):
            for date_field in ["learning_date", "created_at", "updated_at"]:
                if learning.get(date_field):
                    try:
                        date = datetime.fromisoformat(learning[date_field])
                        if date > two_weeks_ago:
                            return True
                    except (ValueError, TypeError):
                        continue
        
        return False
    
    def _identify_blocking_obstacles(self, obstacles: List[Dict]) -> List[Dict]:
        """Identifica obstáculos que están bloqueando el progreso del proyecto"""
        blocking = []
        
        for obstacle in obstacles:
            if obstacle.get("status") != "resolved":
                # Evaluar si es bloqueante basado en varios criterios
                is_blocking = False
                
                # Por prioridad
                if obstacle.get("priority") == "high" or obstacle.get("priority") == "alta":
                    is_blocking = True
                
                # Por impacto
                if obstacle.get("impact") and int(obstacle.get("impact", 0)) >= 4:
                    is_blocking = True
                
                # Por dependencias
                if obstacle.get("dependencies") and len(obstacle.get("dependencies", [])) > 0:
                    is_blocking = True
                
                # Por tiempo bloqueado
                if obstacle.get("created_at"):
                    try:
                        created = datetime.fromisoformat(obstacle["created_at"])
                        if (datetime.utcnow() - created).days > 30:  # Bloqueado por más de 30 días
                            is_blocking = True
                    except (ValueError, TypeError):
                        pass
                
                if is_blocking:
                    blocking.append({
                        "id": obstacle.get("id"),
                        "description": obstacle.get("description", ""),
                        "priority": obstacle.get("priority", ""),
                        "days_open": self._calculate_days_open(obstacle)
                    })
                    
        return blocking