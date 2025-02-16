import unittest
from app.retriever.rank import RankEngine
from app.retriever.types import SearchResult, RankingConfig

class TestRankEngine(unittest.TestCase):
    def setUp(self):
        # Inicializar el RankEngine con una configuración predeterminada
        self.rank = RankEngine(config=RankingConfig())

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
        print("Resultados rankeados:", ranked_results)
        # Verificar que se devuelvan los resultados esperados
        self.assertEqual(len(ranked_results), 3)
        self.assertEqual(ranked_results[0]["id"], "2")  # El resultado con mayor score debe ser el primero

    def test_calculate_adjusted_score(self):
        # Probar el cálculo del score ajustado
        base_score = 0.3
        adjusted_score = self.rank._calculate_adjusted_score(
            base_score=base_score,
            text="Sample text with kata",
            category="challenge",
            keywords=["kata"]
        )
        self.assertGreater(adjusted_score, base_score)
        print(f"Base score: {base_score}, Adjusted score: {adjusted_score}")


if __name__ == '__main__':
    unittest.main()