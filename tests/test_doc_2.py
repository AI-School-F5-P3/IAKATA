# test_documentation.py
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Awaitable
from pathlib import Path
from app.documentation.generator import DocumentGenerator
from app.documentation.templates import TemplateManager
from app.documentation.storage import DocumentStorage
from app.orchestrator.orchestrator import RAGOrchestrator
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
from app.vectorstore.vector_store import VectorStore
from app.documentation.types import DocumentFormat, DocumentType

async def test_format(
    orchestrator: RAGOrchestrator,
    project_data: Dict,
    format: DocumentFormat,
    format_config: Optional[Dict[str, Any]] = None
) -> None:
    """Prueba la generación de documentación en un formato específico"""
    try:
        print(f"\nProbando formato: {format.value}")
        document, formatted_content = await orchestrator.generate_documentation(
            project_data=project_data,
            template_id="project_report",
            format=format,
            format_config=format_config
        )
        
        print(f"✓ Documento generado exitosamente en formato {format.value}")
        print(f"- ID: {document.id}")
        print(f"- Título: {document.title}")
        
        if formatted_content:
            print(f"- Contenido formateado generado: {len(formatted_content)} caracteres")
            if document.metadata.get("formatted_path"):
                print(f"- Guardado en: {document.metadata['formatted_path']}")
                
        return document, formatted_content
        
    except Exception as e:
        print(f"❌ Error probando formato {format.value}: {str(e)}")
        raise

async def test_documentation_generation():
    print("\n=== Iniciando prueba de generación de documentación con múltiples formatos ===\n")
    
    try:
        # 1. Configurar componentes
        print("Configurando componentes...")
        vector_store_dir = Path("app/vectorstore/processed/vectors")
        vector_store = VectorStore()
        vector_store.load(vector_store_dir)
        llm = LLMModule()
        validator = ResponseValidator()
        template_manager = TemplateManager()
        doc_generator = DocumentGenerator(llm)
        doc_storage = DocumentStorage(Path("./test_docs"))

        # 2. Configurar orquestador
        print("Inicializando orquestador...")
        orchestrator = RAGOrchestrator(
            vector_store=vector_store,
            llm=llm,
            validator=validator,
            doc_generator=doc_generator,
            template_manager=template_manager,
            doc_storage=doc_storage
        )

        # 3. Datos de prueba
        project_data = {
            "title": "Mejora del Proceso de Atención al Cliente",
            "type": "challenge",
            "category": "process",
            "description": "Implementación de Lean Kata para optimizar tiempos de respuesta",
            "challenge": {
                "description": "Reducir tiempo de respuesta a tickets de soporte",
                "current_state": "Tiempo promedio actual: 24 horas",
                "target_state": "Tiempo objetivo: 8 horas",
                "category": "challenge",
                "metrics": {
                    "initial": 24,
                    "current": 18,
                    "target": 8
                }
            },
            "experiments": [
                {
                    "id": "EXP001",
                    "category": "experiment",
                    "hypothesis": "Implementar categorización automática reducirá tiempo de asignación",
                    "result": "Reducción de 2 horas en tiempo de asignación",
                    "learning": "La categorización automática es efectiva pero requiere refinamiento"
                }
            ],
            "obstacles": [
                "Alta variabilidad en tipos de tickets",
                "Falta de documentación estandarizada",
                "Dependencia de expertos específicos"
            ],
            "metadata": {
                "category": "process",
                "type": "challenge"
            }
        }

        # 4. Probar diferentes formatos
        
        # 4.1 Markdown (formato simple)
        await test_format(orchestrator, project_data, DocumentFormat.MARKDOWN)

        # 4.2 HTML con configuración personalizada
        html_config = {
            "css_framework": "tailwind",
            "scripts": [
                "https://cdnjs.cloudflare.com/ajax/libs/chart.js/2.9.4/Chart.min.js"
            ]
        }
        await test_format(orchestrator, project_data, DocumentFormat.HTML, html_config)

        # 4.3 PDF con configuración personalizada
        pdf_config = {
            "font_size": 12,
            "margin": 2.0,  # cm
            "template": "report"
        }
        await test_format(orchestrator, project_data, DocumentFormat.PDF, pdf_config)

        # 4.4 JSON con configuración personalizada
        json_config = {
            "indent": 2,
            "ensure_ascii": False
        }
        await test_format(orchestrator, project_data, DocumentFormat.JSON, json_config)
        
        

        print("\n=== Pruebas completadas exitosamente ===")

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_documentation_generation())