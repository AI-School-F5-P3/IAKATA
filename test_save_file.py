from pathlib import Path
from datetime import datetime
from app.documentation.types import Document, DocumentFormat, DocumentType, DocumentSection
from app.documentation.storage import DocumentStorage

def test_save_files():
    """Prueba simple para guardar archivos en diferentes formatos"""
    # Configurar directorio de prueba
    test_dir = Path("./test_files")
    
    # Crear instancia de almacenamiento
    storage = DocumentStorage(base_dir=test_dir)
    
    # Crear un documento simple de prueba
    document = Document(
        id=f"test_{datetime.utcnow().timestamp()}",
        type=DocumentType.REPORT,
        title="Documento de Prueba",
        sections=[
            DocumentSection(
                title="Sección 1",
                content="Contenido de prueba para la sección 1.",
                order=0
            )
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        format=DocumentFormat.MARKDOWN,
        metadata={"test": True}
    )
    
    # Probar diferentes formatos
    formats = [
        DocumentFormat.MARKDOWN,
        DocumentFormat.HTML,
        DocumentFormat.JSON
    ]
    
    print("\n===== PRUEBA DE GUARDADO DE ARCHIVOS =====")
    
    for format_type in formats:
        # Cambiar formato del documento
        document.format = format_type
        
        # Generar contenido simple
        content = f"# {document.title}\n\n## {document.sections[0].title}\n\n{document.sections[0].content}"
        
        # Guardar archivo
        try:
            file_path = storage._save_file(document, content)
            
            # Verificar que se guardó correctamente
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"✓ Archivo {format_type.value} guardado en: {file_path} ({file_size} bytes)")
            else:
                print(f"✗ ERROR: El archivo {file_path} no existe")
        except Exception as e:
            print(f"✗ ERROR guardando {format_type.value}: {str(e)}")
    
    print("\n===== PRUEBA COMPLETADA =====")

if __name__ == "__main__":
    test_save_files()