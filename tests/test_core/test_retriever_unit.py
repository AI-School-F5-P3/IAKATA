import unittest
from unittest import TestCase, mock
from unittest.mock import MagicMock, AsyncMock
from app.retriever.types import SearchResult, BoardSection, SearchQuery, RankingConfig
from app.orchestrator.orchestrator import RAGOrchestrator
from app.llm.types import LLMResponse, ResponseType
from app.retriever.search import SearchEngine
from app.retriever.rank import RankEngine
from app.retriever.retriever import RetrieverSystem
import asyncio
import sys
from pathlib import Path

# Añadimos el directorio src al path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

class TestSearchComponent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Configurar el mock de vector_store
        self.vector_store = AsyncMock()
        self.search_engine = SearchEngine(self.vector_store)

    async def test_search(self):
        # Configurar el mock para que devuelva los resultados esperados
        self.vector_store.hybrid_search.return_value = [
            {"id": "1", "text": "Sample text 1", "score": 0.8, "metadata": {}},
            {"id": "2", "text": "Sample text 2", "score": 0.9, "metadata": {}},
        ]

        # Crear la query de búsqueda
        query = SearchQuery(
            text="How to implement kata?",
            metadata={"category": "challenge"},
            max_results=5
        )

        # Llamar al método search
        results = await self.search_engine.search(query)

        # Verificar que se devuelvan los resultados esperados
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].id, "1")  # Verificar el primer resultado

    async def test_invalid_query(self):
        # Probar que se lance una excepción con una query vacía
        with self.assertRaises(ValueError):
            await self.search_engine.search("")

class TestRankComponent(TestCase):
    def setUp(self):
        # Configurar el RankEngine con un umbral bajo para permitir que los resultados pasen
        self.rank = RankEngine(config=RankingConfig(base_threshold=0.1))

    def test_rank_results(self):
        # Definir los resultados de prueba
        results = [
            SearchResult(id="1", text="Sample text 1", score=0.8, metadata={"category": "challenge"}),
            SearchResult(id="2", text="Sample text 2", score=0.9, metadata={"category": "challenge"}),
            SearchResult(id="3", text="Sample text 3", score=0.7, metadata={"category": "challenge"}),
        ]

        # Llamar al método rank_results
        ranked_results = self.rank.rank_results(
            results=results,
            metadata={"category": "challenge"},
            keywords=[]
        )

        # Verificar que se devuelvan los 3 resultados esperados
        self.assertEqual(len(ranked_results), 3)

        # Verificar que el primer resultado tenga el mayor score
        self.assertEqual(ranked_results[0]["id"], "2")

    def test_empty_results(self):
        # Probar que no se devuelvan resultados si la lista de entrada está vacía
        ranked_results = self.rank.rank_results([], metadata={"category": "challenge"}, keywords=[])
        self.assertEqual(len(ranked_results), 0)

class TestValidateComponent(unittest.TestCase):
    def setUp(self):
        # Crear mocks para las dependencias del orquestador
        self.vector_store = AsyncMock()
        self.llm = MagicMock()
        self.validator = MagicMock()
        
        # Configurar un mock para el método de validación en el LLM
        mock_llm_response = LLMResponse(
            content="Validación exitosa",
            metadata={"model_used": "gpt-4"},
            validation_results={"specific": True, "measurable": True}
        )
        # Configuramos que cuando se invoque validate_board_section en el llm, retorne la respuesta mockeada
        self.llm.validate_board_section = AsyncMock(return_value=mock_llm_response)
        
        # Crear la instancia del orquestador con las dependencias mockeadas
        self.orchestrator = RAGOrchestrator(
            vector_store=self.vector_store,
            llm=self.llm,
            validator=self.validator
        )

    def test_validate_board_content(self):
        # Crear una BoardSection con la categoría en metadata
        section = BoardSection(
            content="Improve production efficiency by 20%",
            metadata={"category": "challenge"}
        )
        # Extraer la categoría y el contenido
        category = section.metadata.get("category")
        content = section.content

        # Llamar al método de validación a través del orquestador
        validation_response = asyncio.run(self.orchestrator.validate_board_section(category, content))
        
        # Imprimir la respuesta (opcional) y realizar aserciones
        print(validation_response)
        self.assertTrue(validation_response.validation_results.get("specific"))
        self.assertTrue(validation_response.validation_results.get("measurable"))

    def test_invalid_board_content(self):
        # Crear una BoardSection con contenido vacío
        section = BoardSection(
            content="",
            metadata={"category": "challenge"}
        )
        category = section.metadata.get("category")
        content = section.content

        # Configurar el mock para que en caso de contenido vacío se lance una excepción
        self.llm.validate_board_section.side_effect = Exception("Contenido vacío")

        with self.assertRaises(Exception):
            asyncio.run(self.orchestrator.validate_board_section(category, content))

if __name__ == '__main__':
    unittest.main()