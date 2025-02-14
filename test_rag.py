import asyncio
import logging
from app.config.logging import setup_logging
from app.orchestrator.orchestrator import RAGOrchestrator
from app.vectorstore.vector_store import VectorStore
from pathlib import Path

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

async def test_board_validation():
    try:
        # Inicializar el orquestador
        rag = RAGOrchestrator()
        
        # Cargar vector store desde los archivos procesados
        vector_store_dir = Path("app/vectorstore/processed/vectors")
        rag.vector_store.load(vector_store_dir)
        
        # Simular una petición de tablero - Challenge
        board_content = {
            "title": "Mejorar eficiencia en línea de producción",
            "description": """
            Necesitamos mejorar la eficiencia de nuestra línea de producción principal
            reduciendo los tiempos de ciclo y minimizando los desperdicios. Actualmente
            tenemos retrasos significativos y alta variabilidad en los procesos.
            """,
            "target_date": "2025-06-30",
            "metrics": {
                "current_cycle_time": 45,
                "target_cycle_time": 30,
                "current_waste_percentage": 15,
                "target_waste_percentage": 5
            }
        }

        # Procesar la petición
        logger.info("Procesando petición de validación de Challenge...")
        response = await rag.process_board_request(
            board_id="TEST-001",
            section_type="challenge",
            content=board_content,
            context={
                "project_type": "manufacturing",
                "team_size": 5,
                "previous_challenges": []
            }
        )

       # Imprimir resultados
        print("\n=== Resultados de la Validación ===")
        print(f"\nContenido de la respuesta:")
        print(response.get("content"))

        if "validation_results" in response:
            print("\nResultados de validación:")
            for key, value in response["validation_results"].items():
                print(f"- {key}: {'✓' if value else '✗'}")

        if "suggestions" in response:
            print("\nSugerencias:")
            for suggestion in response["suggestions"]:
                print(f"- {suggestion}")

        # Paso 2: Verificar la estructura de response antes de acceder a "metadata" y "vector_results"
        if isinstance(response, dict):  # Verifica si response es un diccionario
            if "metadata" in response and "vector_results" in response["metadata"]:  # Verifica si las claves existen
                print("\nContexto recuperado:")
                for result in response["metadata"]["vector_results"]:
                    print(f"\nTexto relevante (score: {result['score']:.2f}):")
                    print(result["text"][:200] + "...")
            else:
                print("\nLa respuesta no contiene 'metadata' o 'vector_results'.")
        else:
            print("\nLa respuesta no es un diccionario:", response)
    except Exception as e:
        logger.error(f"Error durante la ejecución: {str(e)}")
        raise

# Ejecutar el test
if __name__ == "__main__":
    asyncio.run(test_board_validation())