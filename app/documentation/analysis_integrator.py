from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from app.analysis.analyzer import KataAnalyzer, ProjectAnalysis
from app.analysis.db_connector import AnalysisDBConnector 
from app.documentation.generator import DocumentGenerator
from app.documentation.template_manager import TemplateStyleManager
from app.documentation.types import Document, DocumentFormat, DocumentType, DocumentTemplate

logger = logging.getLogger(__name__)

class AnalysisDocumentIntegrator:
    """
    Integra el análisis de proyectos con la generación de documentación
    """
    
    def __init__(
        self, 
        document_generator: DocumentGenerator,
        template_manager: TemplateStyleManager,
        orchestrator=None,
        vector_store=None
    ):
        self.document_generator = document_generator
        self.template_manager = template_manager
        self.orchestrator = orchestrator
        self.vector_store = vector_store
        
    async def generate_analysis_report(
        self,
        project_id: str,
        template_id: str = "project_report",
        format: Optional[DocumentFormat] = None,
        include_raw_metrics: bool = False
    ) -> Document:
        """
        Genera un informe que incluye análisis del proyecto
        
        Args:
            project_id: ID del proyecto a analizar
            template_id: ID del template a utilizar
            format: Formato opcional de salida
            include_raw_metrics: Si es True, incluye métricas en formato técnico
            
        Returns:
            Documento generado con análisis integrado
        """
        try:
            # 1. Obtener plantilla
            template = self.template_manager.get_template(template_id)
            if not template:
                raise ValueError(f"Template no encontrado: {template_id}")
            
            # 2. Obtener análisis del proyecto
            analyzer = self._get_analyzer()
            analysis = await analyzer.analyze_project(project_id)
            
            # 3. Enriquecer contexto con análisis
            enriched_context = self._build_analysis_context(analysis, include_raw_metrics)
            
            # 4. Ajustar plantilla si es necesario para incluir secciones de análisis
            enhanced_template = self._enhance_template_for_analysis(template)
            
            # 5. Generar documento
            document = await self.document_generator.generate_document(
                template=enhanced_template,
                context=enriched_context,
                format=format
            )
            
            # Añadir metadatos de análisis
            document.metadata = document.metadata or {}
            document.metadata["analysis_id"] = str(analysis.analyzed_at.timestamp())
            document.metadata["project_name"] = analysis.project_name
            document.metadata["overall_score"] = analysis.metrics.overall_score
            
            return document
            
        except Exception as e:
            logger.error(f"Error generando informe con análisis: {str(e)}")
            raise
            
    def _get_analyzer(self) -> KataAnalyzer:
        """Obtiene o crea un analizador de proyectos"""
        if not hasattr(self, '_analyzer'):
            if not self.orchestrator or not self.vector_store:
                # Si no se proporcionaron componentes, obtenerlos del servicio
                from app.api.services.chat_services import get_components
                components = get_components()
                orchestrator = components["orchestrator"]
                vector_store = components["vector_store"]
            else:
                orchestrator = self.orchestrator
                vector_store = self.vector_store
                
            # Crear el analizador
            self._analyzer = KataAnalyzer(
                orchestrator=orchestrator,
                vector_store=vector_store,
                db_connector=AnalysisDBConnector()
            )
            
        return self._analyzer
        
    def _build_analysis_context(
        self, 
        analysis: ProjectAnalysis,
        include_raw_metrics: bool = False
    ) -> Dict[str, Any]:
        """
        Construye el contexto para la generación del documento
        
        Args:
            analysis: Análisis del proyecto
            include_raw_metrics: Si es True, incluye métricas técnicas
            
        Returns:
            Contexto enriquecido para generación de documento
        """
        # Preparar métricas en formato amigable
        formatted_metrics = analysis.metrics.to_display_dict()
        
        # Agrupar insights por tipo
        insights_by_type = {
            "strength": [],
            "improvement": [],
            "risk": []
        }
        
        for insight in analysis.insights:
            if insight.type in insights_by_type:
                insights_by_type[insight.type].append({
                    "description": insight.description,
                    "importance": insight.importance,
                    "related_metric": insight.related_metric
                })
        
        # Construir contexto
        context = {
            "project": {
                "id": analysis.project_id,
                "name": analysis.project_name,
                "analyzed_at": analysis.analyzed_at.strftime("%Y-%m-%d %H:%M"),
                "status": analysis.status.status,
                "trend": analysis.trend()
            },
            "metrics": formatted_metrics,
            "insights": {
                "strengths": insights_by_type["strength"],
                "improvements": insights_by_type["improvement"],
                "risks": insights_by_type["risk"]
            },
            "recommendations": [
                {
                    "action": rec.action,
                    "priority": rec.priority,
                    "impact": rec.impact,
                    "estimated_time": rec.estimated_time
                }
                for rec in analysis.recommendations
            ],
            "coaching_needs": analysis.status.coaching_needs,
            "blocking_obstacles": analysis.status.blocking_obstacles,
            "risk_factors": analysis.status.risk_factors
        }
        
        # Opcionalmente incluir métricas en formato técnico
        if include_raw_metrics:
            context["raw_metrics"] = analysis.metrics.dict()
            
        return context
    
    def _enhance_template_for_analysis(
        self, 
        template: DocumentTemplate
    ) -> DocumentTemplate:
        """
        Mejora un template para incluir secciones relevantes de análisis
        
        Args:
            template: Template original
            
        Returns:
            Template mejorado con secciones de análisis
        """
        # Si ya es un template específico para análisis, usarlo tal cual
        if template.id.startswith("analysis_"):
            return template
            
        # Copiar el template
        enhanced_sections = list(template.sections)
        
        # Verificar si ya tiene secciones de análisis
        has_metrics = any("métricas" in section.lower() for section in enhanced_sections)
        has_recommendations = any("recomendaciones" in section.lower() for section in enhanced_sections)
        
        # Añadir secciones de análisis si no las tiene
        if not has_metrics:
            enhanced_sections.append("Métricas y Estado del Proyecto")
        
        if not has_recommendations:
            enhanced_sections.append("Recomendaciones")
        
        # Crear template mejorado
        return DocumentTemplate(
            id=f"analysis_{template.id}",
            name=f"Análisis: {template.name}",
            type=template.type,
            sections=enhanced_sections,
            format=template.format,
            metadata={
                "original_template_id": template.id,
                "enhanced_for_analysis": True
            }
        )