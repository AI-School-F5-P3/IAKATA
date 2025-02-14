# tests/test_vector_store.py
import unittest
from app.vectorstore.vector_store import VectorStore

class TestVectorStore(unittest.TestCase):
    def setUp(self):
        self.vector_store = VectorStore()
        self.vector_store.section_chunks = {
            'section_1': ['chunk_1', 'chunk_2', 'chunk_3']
        }
        self.vector_store.chunk_relations = {
            'chunk_1': {'next_chunk': 'chunk_2'},
            'chunk_2': {'prev_chunk': 'chunk_1', 'next_chunk': 'chunk_3'},
            'chunk_3': {'prev_chunk': 'chunk_2'}
        }

    def test_get_chunk_context(self):
        metadata = {'chunk_info': {'section_id': 'section_1'}}
        context = self.vector_store._get_chunk_context('chunk_2', metadata)
        self.assertIsInstance(context, dict)
        self.assertIsInstance(context['section_chunks'], list)
        self.assertIsInstance(context['relations'], dict)
        self.assertIsInstance(context['position'], dict)
        self.assertEqual(context['position']['index'], 1)
        self.assertEqual(context['position']['total'], 3)
        self.assertFalse(context['position']['is_first'])
        self.assertFalse(context['position']['is_last'])

if __name__ == '__main__':
    unittest.main()