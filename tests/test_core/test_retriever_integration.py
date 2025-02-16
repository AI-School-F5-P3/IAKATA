import unittest
from unittest.mock import MagicMock, patch
from app.retriever.retriever import RetrieverSystem
from app.retriever.types import BoardSection, RetrieverResponse
from app.llm.types import ResponseType

class TestRetrieverIntegration(unittest.IsolatedAsyncioTestCase):  # Clase asíncrona de unittest
    def setUp(self):  # Sin `async`
        self.vector_store = MagicMock()
        self.retriever_system = RetrieverSystem(self.vector_store)

    @patch('app.retriever.search.SearchEngine.search')
    @patch('app.retriever.rank.RankEngine.rank_results')
    @patch('app.retriever.filter.FilterSystem.filter_results')
    async def test_process_board_section(self, mock_filter, mock_rank, mock_search):
        mock_search.return_value = [
            {"id": "1", "text": "Sample text 1", "score": 0.8, "metadata": {}},
            {"id": "2", "text": "Sample text 2", "score": 0.9, "metadata": {}},
        ]
        mock_rank.return_value = [
            {"id": "1", "text": "Sample text 1", "score": 0.8, "metadata": {}},
            {"id": "2", "text": "Sample text 2", "score": 0.9, "metadata": {}},
        ]
        mock_filter.return_value = {
            "search_results": [{"id": "1", "text": "Sample text 1", "score": 0.8, "metadata": {}}],
            "response_type": ResponseType.VALIDATION,
            "validation_criteria": {"specific": "Debe ser específico y claro"}
        }

        section = BoardSection(section_type="challenge", content="Improve efficiency", metadata={"author": "user1"})
        response = await self.retriever_system.process_board_section(section)  # Usar await aquí

        self.assertIsInstance(response, RetrieverResponse)
        self.assertEqual(response.section_type, "challenge")
        self.assertEqual(response.response_type, ResponseType.VALIDATION)

if __name__ == '__main__':
    unittest.main()
