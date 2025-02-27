# test_documentation.py
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Awaitable
from pathlib import Path
from app.documentation.generator import DocumentGenerator
from app.documentation.template_manager import TemplateStyleManager
from app.documentation.storage import DocumentStorage
from app.orchestrator.orchestrator import RAGOrchestrator
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
from app.vectorstore.vector_store import VectorStore
from app.documentation.types import DocumentFormat

async def test_documentation_generation():
    print("\n=== Iniciando prueba de generación de documentación ===\n")
    
    try:
        # 1. Configurar componentes
        print("Configurando componentes...")
        vector_store_dir = Path("app/vectorstore/processed/vectors")
        vector_store = VectorStore()
        vector_store.load(vector_store_dir)
        llm = LLMModule()
        validator = ResponseValidator()
        template_manager = TemplateStyleManager()
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

        # 3. Datos de prueba - Un proyecto Lean Kata realista
        # project_data en test_documentation.py
        
        project_data = {
            "title": "Mejora del Proceso de Atención al Cliente",
            "type": "challenge",  # Tipo de proyecto
            "category": "process",  # Categoría explícita
            "description": "Implementación de Lean Kata para optimizar tiempos de respuesta",
            "challenge": {
                "description": "Reducir tiempo de respuesta a tickets de soporte",
                "current_state": "Tiempo promedio actual: 24 horas",
                "target_state": "Tiempo objetivo: 8 horas",
                "category": "challenge",  # Categoría para esta sección
                "metrics": {
                    "initial": 24,
                    "current": 18,
                    "target": 8
                }
            },
            "experiments": [
                {
                    "id": "EXP001",
                    "category": "experiment",  # Categoría para experimentos
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
                "category": "process",  # Categoría en metadata
                "type": "challenge"
            }
        }

        # 4. Generar documentación
        print("\nGenerando documentación...")
        document = await orchestrator.generate_documentation(
            project_data=project_data,
            template_id="project_report",
            format=DocumentFormat.MARKDOWN
        )

        # 5. Verificar resultado
        print("\nVerificando documento generado:")
        print(f"- ID: {document.id}")
        print(f"- Título: {document.title}")
        print(f"- Formato: {document.format.value}")
        print(f"- Número de secciones: {len(document.sections)}")
        print("\nSecciones generadas:")
        for section in document.sections:
            print(f"\n=== {section.title} ===")
            print(f"Longitud del contenido: {len(section.content)} caracteres")
            print("Primeros 100 caracteres:", section.content[:100], "...")

        if document.metadata and "file_path" in document.metadata:
            print(f"\nDocumento guardado en: {document.metadata['file_path']}")

        print("\n=== Prueba completada exitosamente ===")
        return document

    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_documentation_generation())