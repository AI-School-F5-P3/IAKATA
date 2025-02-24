from pathlib import Path
from app.core.knowledge.processors.pdf_processor import PDFProcessor
from app.core.knowledge.analyzers.structure_analyzer import StructureAnalyzer, save_structure_analysis
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Definir las rutas de los PDFs
pdf_paths = [
    str(BASE_DIR / "sources/books/toyota_kata.pdf"),
    str(BASE_DIR / "sources/books/670400971-Lean-Kata-de-Los-Procesos-a-Las-Personas-Spanish-Edition-a2020.pdf")
]

def save_analysis(analysis: dict, output_dir: Path):
    """Guarda los resultados del análisis"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"extraction_results_{timestamp}.json"
    
    # Asegurar que el directorio existe
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    return output_file

if __name__ == "__main__":
    try:
        print("\nIniciando procesamiento de libros...")
        
        # Fase 1: Extracción
        processor = PDFProcessor()
        extraction = processor.analyze_books(pdf_paths)
        
        # Guardar resultados de extracción
        output_dir = BASE_DIR / "processed/books"
        extraction_file = save_analysis(extraction, output_dir)
        
        print("\n=== Extracción Completada ===")
        print(f"Resultados guardados en: {extraction_file}")
        
        # Fase 2: Análisis de Estructura
        print("\nIniciando análisis de estructura...")
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("No se encontró OPENAI_API_KEY en el archivo .env")
        
        analyzer = StructureAnalyzer(api_key)
        structure_analysis = analyzer.analyze_books_structure(extraction_file)
        
        # Guardar resultados del análisis de estructura
        structure_file = save_structure_analysis(structure_analysis, output_dir)
        
        print("\n=== Análisis de Estructura Completado ===")
        print(f"Resultados guardados en: {structure_file}")
        
    except Exception as e:
        print(f"\nError durante el procesamiento: {str(e)}")