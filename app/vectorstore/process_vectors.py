from pathlib import Path
import logging
from vector_store import VectorStore
from typing import Dict, Any, Optional
import json
from tqdm import tqdm
from text_processor import TextProcessor
from common_types import ProcessedText, TextType

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rutas
BASE_DIR = Path(__file__).resolve().parent
STRUCTURE_FILE = Path(r"C:\Users\samir\IAKATA\app\knowledge\processed\books\structure_analysis.json")
VECTORS_DIR = BASE_DIR / "processed/vectors"

def validate_paths() -> None:
    """Valida que existan las rutas necesarias"""
    logger.info("Validando rutas...")
    if not STRUCTURE_FILE.exists():
        raise FileNotFoundError(f"No se encontró el archivo de estructura: {STRUCTURE_FILE}")
    
    VECTORS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Rutas validadas correctamente")

def verify_structure_file() -> None:
    """Verifica la estructura del archivo JSON"""
    try:
        logger.info("Verificando estructura del archivo JSON...")
        with open(STRUCTURE_FILE, 'r', encoding='utf-8') as f:
            structure = json.load(f)
        
        if 'books_analysis' not in structure:
            raise ValueError("El archivo no contiene la estructura esperada (books_analysis)")
            
        if not structure['books_analysis']:
            raise ValueError("No hay libros para analizar en el archivo")
            
        logger.info("Estructura del archivo JSON verificada correctamente")
            
    except json.JSONDecodeError:
        raise ValueError(f"El archivo {STRUCTURE_FILE} no es un JSON válido")

def print_stats(stats: Dict[str, Any]) -> None:
    """Imprime las estadísticas del procesamiento"""
    logger.info("\nEstadísticas finales:")
    stats_to_show = {
        'Total de vectores': stats['total_vectores'],
        'Dimensión de vectores': stats['dimension_vectores'],
        'Total de batches': stats['total_batches'],
        'Tamaño de batch': stats['batch_size'],
        'Textos exitosos': stats['textos_exitosos'],
        'Textos fallidos': stats['textos_fallidos'],
        'Tasa de éxito': f"{stats['tasa_exito']:.2f}%"
    }
    
    for key, value in stats_to_show.items():
        logger.info(f"{key}: {value}")

def test_search(vector_store: VectorStore) -> None:
    """Realiza múltiples búsquedas de prueba con diferentes tipos de preguntas"""
    test_queries = [
        "¿Cómo implementar Lean Kata en la práctica?",
        "¿Qué es Lean Kata y cuáles son sus principios?",
        "¿Por qué deberíamos implementar Lean Kata en nuestra organización?",
        "¿Cuáles son los pasos específicos del método Lean Kata?"
    ]
    
    for query in test_queries:
        try:
            logger.info(f"\nRealizando búsqueda de prueba con query: '{query}'")
            
            results = vector_store.hybrid_search(query)
            
            if not results:
                logger.warning(f"No se encontraron resultados para: {query}")
                continue
                
            logger.info("\nResultados de prueba:")
            for i, result in enumerate(results, 1):
                logger.info(f"\n{i}. Score: {result['score']:.3f}")
                logger.info(f"ID: {result['id']}")
                logger.info(f"Tipo: {result.get('type', 'No especificado')}")
                logger.info(f"Texto: {result['text'][:200]}...")
                
            logger.info("\n" + "-"*80 + "\n")  # Separador entre queries
                
        except Exception as e:
            logger.error(f"Error en búsqueda de prueba para query '{query}': {e}", exc_info=True)

def main():
    try:
        logger.info("Iniciando proceso de vectorización...")
        
        # Validar configuración inicial
        validate_paths()
        verify_structure_file()
        
        # Configuración
        batch_size = 32
        model_name = 'all-MiniLM-L6-v2'
        chunk_size = 512
        chunk_overlap = 50
        
        # Crear Vector Store
        logger.info("Inicializando Vector Store...")
        vector_store = VectorStore(
            model_name=model_name,
            batch_size=batch_size,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Procesar y vectorizar
        logger.info("Iniciando procesamiento de documentos...")
        stats = vector_store.process_and_index(STRUCTURE_FILE)
        
        # Guardar resultados
        logger.info("Guardando vectores y metadatos...")
        vector_store.save(VECTORS_DIR)
        
        # Mostrar estadísticas
        print_stats(stats)
        
        # Realizar búsqueda de prueba
        test_search(vector_store)
        
        logger.info("Procesamiento completado exitosamente")
        
    except FileNotFoundError as e:
        logger.error(f"Error de archivo: {e}")
        raise
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        raise
    except Exception as e:
        logger.error(f"Error en procesamiento: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Error fatal en la ejecución:", exc_info=True)
        raise