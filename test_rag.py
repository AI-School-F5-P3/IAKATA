import asyncio
import logging
from app.config.logging import setup_logging
from app.orchestrator.orchestrator import RAGOrchestrator
from app.vectorstore.vector_store import VectorStore
from app.retriever.search import SearchEngine
from app.llm.types import LLMResponse
from app.llm.gpt import LLMModule
from pathlib import Path
from unittest.mock import AsyncMock

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

async def test_board_validation():
    try:
        # Inicializar vector store y search engine
        vector_store_dir = Path("app/vectorstore/processed/vectors")
        vector_store = VectorStore()
        vector_store.load(vector_store_dir)
        search_engine = SearchEngine(vector_store)

        # Inicializar el LLM real
        llm = LLMModule()
        validator = llm.validator

        # Inicializar el orquestador con las instancias actualizadas
        rag = RAGOrchestrator(
            vector_store=vector_store,  # Todavía necesitamos vector_store para otras operaciones
            llm=llm,
            validator=validator
        )

        # Simular board content
        board_content = {
            "title": "Mejorar eficiencia en línea de producción",
            "description": """
            Necesitamos mejorar la eficiencia de nuestra línea de producción principal
            reduciendo los tiempos de ciclo y minimizando los desperdicios.
            """
        }
        context = {
            "project_type": "manufacturing",
            "team_size": 5,
            "previous_challenges": []
        }

        # Llamar al método de procesamiento
        response = await rag.process_board_request(
            board_id="TEST-001",
            section_type="challenge",
            content=board_content,
            context=context
        )

        # Imprimir resultados de la respuesta
        print("\n=== Resultados de la Validación ===")
        print(f"Contenido de la respuesta:\n{response.content}")

        if response.validation_results:
            print("\nEstado de la validación:")
            for key, value in response.validation_results.items():
                if key != 'validation_error':
                    print(f"- {key}: {'✓' if value else '✗'}")

        if response.suggestions:
            print("\nSugerencias:")
            for suggestion in response.suggestions:
                print(f"- {suggestion}")

        if response.metadata and "sources" in response.metadata:
            print("\nFuentes utilizadas:")
            for source in response.metadata["sources"]:
                print(f"- ID: {source['id']} (Score: {source['score']:.2f})")

        if response.validation_results and 'validation_error' in response.validation_results:
            print(f"\nError de validación: {response.validation_results['validation_error']}")

    except Exception as e:
        logger.error(f"Error durante la ejecución: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_board_validation())