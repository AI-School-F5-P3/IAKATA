# tests/test_core/test_filter.py
import unittest
from unittest.mock import MagicMock
from app.retriever.filter import FilterSystem
from app.retriever.types import FilterConfig
from app.llm.types import ResponseType

class TestFilterSystem(unittest.TestCase):
    def setUp(self):
        self.config = FilterConfig(min_score=0.5, max_results=3)
        self.filter_system = FilterSystem(self.config)

    def test_apply_basic_filters(self):
        results = [
            {"text": "Sample text 1", "score": 0.7, "metadata": {"author": "user1"}},
            {"text": "Sample text 2", "score": 0.4, "metadata": {"author": "user2"}},
            {"text": "Sample text 3", "score": 0.8, "metadata": {"author": "user3"}},
        ]
        filtered = self.filter_system._apply_basic_filters(results)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["text"], "Sample text 1")

    def test_get_response_type(self):
        response_type = self.filter_system._get_response_type("challenge")
        self.assertEqual(response_type, ResponseType.VALIDATION)

    def test_extract_suggestions(self):
        results = [
            {"text": "Considera desglosar el desafío. Deberías definir métricas."},
            {"text": "Es recomendable alinearse con los objetivos estratégicos."},
        ]
        suggestions = self.filter_system._extract_suggestions(results)
        self.assertEqual(len(suggestions), 3)
        self.assertIn("Considera desglosar el desafío", suggestions)
        self.assertIn("Deberías definir métricas", suggestions)
        
    def test_get_validation_criteria(self):
        criteria = self.filter_system._get_validation_criteria("target")
        self.assertIn("timebound", criteria)
        self.assertIn("achievable", criteria)

if __name__ == '__main__':
    unittest.main()