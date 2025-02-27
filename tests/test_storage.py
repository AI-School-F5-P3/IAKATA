from pathlib import Path
from app.documentation.storage import DocumentStorage
from app.documentation.types import Document, DocumentType, DocumentFormat, DocumentSection
from datetime import datetime

# Crear una instancia de storage con un directorio de prueba
test_dir = Path("./test_storage_verification")
storage = DocumentStorage(base_dir=test_dir)

# Verificar que los directorios se han creado
for format_type, dir_path in storage.dirs.items():
    print(f"Directorio para {format_type.value}: {dir_path}")
    print(f"¿Existe? {dir_path.exists()}")

def create_test_document(format_type: DocumentFormat):
    return Document(
        id=f"test_{format_type.value}_{datetime.utcnow().timestamp()}",
        type=DocumentType.REPORT,
        title=f"Test Document - {format_type.value}",
        sections=[
            DocumentSection(
                title="Test Section",
                content="This is a test section content.",
                order=0
            )
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        format=format_type,
        metadata={"test": True}
    )


# Probar cada formato
formats_to_test = [
    DocumentFormat.MARKDOWN,
    DocumentFormat.HTML,
    DocumentFormat.JSON,
    DocumentFormat.PDF,
    DocumentFormat.EXCEL
]

for format_type in formats_to_test:
    document = create_test_document(format_type)
    
    # Generar contenido de prueba
    content = f"Test content for {format_type.value} format"
    
    # Intentar guardar el archivo
    try:
        file_path = storage._save_file(document, content)
        print(f"Archivo {format_type.value} guardado en: {file_path}")
        print(f"¿Existe el archivo? {file_path.exists()}")
        print(f"Tamaño del archivo: {file_path.stat().st_size} bytes")
    except Exception as e:
        print(f"Error guardando {format_type.value}: {e}")

    