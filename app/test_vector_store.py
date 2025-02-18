from pathlib import Path
import logging
from app.vectorstore.vector_store import VectorStore
from typing import Dict, Any, Optional
import json
from tqdm import tqdm
from app.vectorstore.text_processor import TextProcessor
from app.vectorstore.common_types import ProcessedText, TextType

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rutas
BASE_DIR = Path(__file__).resolve().parent
STRUCTURE_FILE = BASE_DIR / "knowledge/processed/books/structure_analysis.json"
VECTORS_DIR = BASE_DIR / "vectorstore/processed/vectors"

def test_vector_store():
    """Test de inicialización y carga del vector store"""
    try:
        logger.info("Iniciando test de vector store...")
        
        # 1. Verificar directorios y archivos
        if not STRUCTURE_FILE.exists():
            logger.error(f"No se encontró el archivo de estructura: {STRUCTURE_FILE}")
            return
            
        VECTORS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 2. Cargar análisis estructural
        with open(STRUCTURE_FILE, 'r', encoding='utf-8') as f:
            structure = json.load(f)
            
        if 'books_analysis' not in structure:
            logger.error("El archivo no contiene la estructura esperada")
            return
            
        # 3. Inicializar Vector Store
        vector_store = VectorStore()
        
        # 4. Cargar o procesar vectores
        if (VECTORS_DIR / "faiss.index").exists():
            logger.info("Cargando vectores existentes...")
            vector_store.load(VECTORS_DIR)
        else:
            logger.info("Procesando y vectorizando contenido...")
            stats = vector_store.process_and_index(STRUCTURE_FILE)
            vector_store.save(VECTORS_DIR)
            logger.info(f"Estadísticas de procesamiento: {stats}")
            
        # 5. Probar búsqueda
        test_queries = [
            "¿Qué es Lean Kata?",
            "¿Cómo implementar Lean Kata en la práctica?",
            "¿Cuáles son los pasos del método Lean Kata?"
        ]
        
        for query in test_queries:
            logger.info(f"\nProbando búsqueda: '{query}'")
            results = vector_store.hybrid_search(query, top_k=3)
            
            if results:
                logger.info(f"Encontrados {len(results)} resultados:")
                for i, result in enumerate(results, 1):
                    logger.info(f"\n{i}. Score: {result['score']:.3f}")
                    logger.info(f"Texto: {result['text'][:200]}...")
            else:
                logger.warning("No se encontraron resultados")
                
        logger.info("\nTest completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en test: {str(e)}")
        raise

if __name__ == "__main__":
    test_vector_store()