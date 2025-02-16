# tests/test_core/test_search.py
import unittest
from unittest.mock import AsyncMock
from app.retriever.search import SearchEngine
from app.retriever.types import SearchQuery
from typing import Dict, List, Optional
import asyncio


class TestSearchEngine(unittest.IsolatedAsyncioTestCase):
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

        # Verificar que se devuelvan exactamente 2 resultados
        self.assertEqual(len(results), 2)

        # Verificar que los IDs de los resultados sean los esperados
        self.assertEqual(results[0].id, "1")
        self.assertEqual(results[1].id, "2")
        print("Resultados de la búsqueda:", results)
        
    def test_enrich_query(self):
        # Probar el método _enrich_query
        enriched_query = self.search_engine._enrich_query(
            "Improve efficiency",
            metadata={"category": "challenge"}
        )
        self.assertIn("Relacionado con:", enriched_query)


if __name__ == '__main__':
    unittest.main()