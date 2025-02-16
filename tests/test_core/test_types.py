import unittest
from app.llm.types import ResponseType
from app.retriever.types import BoardSection, SearchQuery, SearchResult, RankingConfig, FilterConfig, RetrieverResponse

class TestTypes(unittest.TestCase):
    def test_board_section(self):
        # En lugar de pasar "section_type", se almacena la categoría en metadata
        section = BoardSection(
            content="Improve efficiency",
            metadata={"category": "challenge", "author": "user1"}
        )
        # Se verifica que en metadata exista la clave "category" con el valor esperado
        self.assertEqual(section.metadata.get("category"), "challenge")
        self.assertEqual(section.content, "Improve efficiency")

    def test_search_query(self):
        # Se usa metadata para indicar la categoría
        query = SearchQuery(
            text="How to implement kata?",
            metadata={"category": "challenge"},
            max_results=5
        )
        self.assertEqual(query.text, "How to implement kata?")
        self.assertEqual(query.metadata.get("category"), "challenge")

    def test_search_result(self):
        result = SearchResult(
            id="1", 
            text="Sample text", 
            score=0.8, 
            metadata={"author": "user1"}
        )
        self.assertEqual(result.id, "1")
        self.assertEqual(result.text, "Sample text")

    def test_ranking_config(self):
        config = RankingConfig(base_threshold=0.5, keyword_boost=0.1, max_score=1.0)
        self.assertEqual(config.base_threshold, 0.5)

    def test_filter_config(self):
        config = FilterConfig(min_score=0.5, max_results=5)
        self.assertEqual(config.min_score, 0.5)

    def test_retriever_response(self):
        # Se crea la respuesta usando metadata para almacenar la categoría
        response = RetrieverResponse(
            response_type=ResponseType.VALIDATION,
            search_results=[{"id": "1", "text": "Sample text", "score": 0.8}],
            suggestions=["Consider breaking down the challenge"],
            validation_criteria={"specific": "Debe ser específico y claro"},
            metadata={"category": "challenge"}
        )
        self.assertEqual(response.metadata.get("category"), "challenge")
        self.assertEqual(response.response_type, ResponseType.VALIDATION)

if __name__ == '__main__':
    unittest.main()
