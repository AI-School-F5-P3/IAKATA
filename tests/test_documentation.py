import asyncio
import pytest
from pathlib import Path
from datetime import datetime
import json

# Importaciones del sistema de documentación
from app.documentation.types import DocumentType, DocumentFormat, Document, DocumentSection
from app.documentation.generator import DocumentGenerator
from app.documentation.format_handler import FormatHandler
from app.documentation.template_manager import TemplateStyleManager, ReportStyle
from app.documentation.service import DocumentationService
from app.documentation.storage import DocumentStorage

# Mock para simular dependencias del orquestador RAG
class MockLLM:
    async def process_request(self, request):
        # Simulamos una respuesta del LLM para generar contenido
        content = f"Contenido generado para la sección '{request.query}'"
        return type('LLMResponse', (), {'content': content})

class MockVectorStore:
    def __init__(self):
        pass

class MockOrchestrator:
    def __init__(self):
        self.llm = MockLLM()
        
    async def process_query(self, query, response_type, metadata=None):
        content = f"Contenido enriquecido para la búsqueda: {query}"
        return type('LLMResponse', (), {'content': content, 'confidence': 0.85})

@pytest.fixture
def doc_service():
    # Crear instancias necesarias para el servicio
    vector_store = MockVectorStore()
    orchestrator = MockOrchestrator()
    base_dir = Path("./test_docs")
    
    # Limpiar y crear directorio de prueba
    if base_dir.exists():
        for file in base_dir.glob("**/*"):
            if file.is_file():
                file.unlink()
    else:
        base_dir.mkdir(parents=True, exist_ok=True)
    
    # Crear almacenamiento solo con sistema de archivos
    storage = DocumentStorage(base_dir=base_dir)
    
    # Crear componentes del servicio
    template_manager = TemplateStyleManager()
    generator = DocumentGenerator(orchestrator.llm)
    format_handler = FormatHandler()
    
    # Crear servicio personalizado para pruebas
    service = DocumentationService(
        vector_store=vector_store,
        rag_orchestrator=orchestrator,
        base_dir=base_dir
    )
    
    # Reemplazar componentes con nuestras versiones de prueba
    service.storage = storage
    service.generator = generator
    service.format_handler = format_handler
    service.template_manager = template_manager
    
    return service

@pytest.fixture
def format_handler():
    return FormatHandler()

def create_test_document():
    """Crea un documento de prueba para las conversiones de formato"""
    return Document(
        id=f"test_{datetime.utcnow().timestamp()}",
        type=DocumentType.REPORT,
        title="Informe de Prueba de Formatos",
        sections=[
            DocumentSection(
                title="Sección 1",
                content="Este es el contenido de prueba para la sección 1.",
                order=0
            ),
            DocumentSection(
                title="Sección 2",
                content="Este es el contenido de prueba para la sección 2.\n* Punto 1\n* Punto 2",
                order=1
            )
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        format=DocumentFormat.MARKDOWN,
        metadata={"test": True, "author": "Test Script"}
    )


async def test_document_format_conversion(format_handler):
    """Prueba la conversión de un documento entre diferentes formatos"""
    # Crear documento de prueba
    document = create_test_document()
    
    # Probar conversión a diferentes formatos
    markdown = format_handler.format_document(document, DocumentFormat.MARKDOWN)
    html = format_handler.format_document(document, DocumentFormat.HTML)
    pdf_content = format_handler.format_document(document, DocumentFormat.PDF)
    excel_content = format_handler.format_document(document, DocumentFormat.EXCEL)
    
    # Verificar que todos los formatos contienen el título del documento
    assert document.title in markdown
    assert document.title in html
    assert document.title in pdf_content
    
    # Verificar JSON estructura correcta para Excel
    excel_data = json.loads(excel_content)
    assert excel_data["metadata"]["title"] == document.title
    
    # Verificar que las secciones están presentes
    for section in document.sections:
        assert section.title in markdown
        assert section.title in html
        assert section.title in pdf_content
        assert any(s["title"] == section.title for s in excel_data["sections"])
    
    print("\nPrueba de conversión de formatos exitosa!")
    print(f"Tamaño de Markdown: {len(markdown)} caracteres")
    print(f"Tamaño de HTML: {len(html)} caracteres")
    print(f"Tamaño de PDF-ready: {len(pdf_content)} caracteres")
    print(f"Tamaño de Excel-ready: {len(excel_content)} caracteres")

async def test_generate_report_with_format_choice(doc_service):
    """Prueba la generación de un reporte eligiendo diferentes formatos"""
    # Datos de proyecto de ejemplo
    project_data = {
        "title": "Proyecto de Mejora de Procesos",
        "description": "Implementación de metodología Lean Kata en el departamento de producción",
        "challenge": {
            "description": "Reducir el tiempo de ciclo en 20%",
            "current_state": "Tiempo de ciclo actual: 45 minutos",
            "target_state": "Tiempo de ciclo objetivo: 36 minutos"
        }
    }
    
    # Probar con diferentes formatos
    formats = ["markdown", "html", "pdf", "json"]
    reports = {}
    
    for format_name in formats:
        result = await doc_service.generate_project_report(
            project_data=project_data,
            template_id="project_summary",  # Usar la plantilla resumida para la prueba
            style="default",
            output_format=format_name
        )
        
        reports[format_name] = result
        print(f"\nReporte generado en formato {format_name}:")
        print(f"ID: {result['document_id']}")
        print(f"Ruta: {result['file_path']}")
        
        # Verificar que el archivo se ha guardado correctamente
        file_path = Path(result["file_path"])
        assert file_path.exists(), f"El archivo {file_path} no existe"
        assert file_path.stat().st_size > 0, f"El archivo {file_path} está vacío"
    
    # Verificar que se generaron todos los formatos
    assert len(reports) == len(formats)
    
    # Verificar que las rutas de archivo tienen las extensiones correctas
    for format_name, report in reports.items():
        if format_name == "markdown":
            assert report["file_path"].endswith(".md")
        elif format_name == "html":
            assert report["file_path"].endswith(".html")
        elif format_name == "pdf":
            assert report["file_path"].endswith(".pdf")
        elif format_name == "json":
            assert report["file_path"].endswith(".json")
    
    print("\nPrueba de generación de reportes en diferentes formatos exitosa!")

async def test_convert_existing_document(doc_service):
    """Prueba la conversión de un documento existente a otro formato"""
    # Primero generamos un documento en markdown
    project_data = {
        "title": "Documento para conversión",
        "description": "Este documento se convertirá a otros formatos",
    }
    
    # Generar documento original en markdown
    original = await doc_service.generate_project_report(
        project_data=project_data,
        template_id="project_summary",
        style="default",
        output_format="markdown"
    )
    
    original_id = original["document_id"]
    print(f"\nDocumento original generado con ID: {original_id}")
    
    # Convertir a otros formatos
    target_formats = ["html", "pdf", "json"]
    conversions = []
    
    for target_format in target_formats:
        conversion = await doc_service.convert_document_format(
            document_id=original_id,
            target_format=target_format
        )
        
        conversions.append(conversion)
        print(f"Convertido a {target_format}: {conversion['new_id']}")
        
        # Verificar que el archivo convertido existe
        file_path = Path(conversion["file_path"])
        assert file_path.exists(), f"El archivo {file_path} no existe"
        assert file_path.stat().st_size > 0, f"El archivo {file_path} está vacío"
    
    # Verificar que se realizaron todas las conversiones
    assert len(conversions) == len(target_formats)
    
    # Verificar que todos los formatos son diferentes al original
    for conversion in conversions:
        assert conversion["original_format"] != conversion["new_format"]
    
    print("\nPrueba de conversión de documentos existentes exitosa!")

async def test_detailed_report_flow(doc_service):
    """Prueba detallada que registra el flujo de información durante la generación de reportes"""
    print("\n=== VERIFICACIÓN DEL FLUJO DE INFORMACIÓN ===")
    
    # Datos de proyecto de ejemplo
    project_data = {
        "title": "Proyecto de Verificación de Flujo",
        "description": "Proyecto para verificar el flujo de datos en la generación de reportes",
        "challenge": {
            "description": "Verificar flujo de información",
            "target_state": "Flujo verificado y funcionando correctamente"
        }
    }
    
    # 1. Iniciar generación
    print("\n1. INICIANDO GENERACIÓN DE REPORTE")
    print(f"   Datos del proyecto: {project_data['title']}")
    print(f"   Plantilla solicitada: project_summary")
    print(f"   Formato solicitado: html")
    
    # 2. Orquestación y enriquecimiento de contexto
    # Sobreescribir métodos internos para añadir logs
    original_build_context = doc_service._build_documentation_context
    
    async def logged_build_context(project_data):
        print("\n2. ENRIQUECIENDO CONTEXTO")
        print(f"   Extrayendo términos de búsqueda para RAG...")
        context = await original_build_context(project_data)
        print(f"   Contexto enriquecido generado: {len(str(context))} caracteres")
        print(f"   Metadatos disponibles: {list(context.get('metadata', {}).keys())}")
        return context
    
    doc_service._build_documentation_context = logged_build_context
    
    # 3. Guardar método original de generación y sobreescribir
    original_generate = doc_service.generator.generate_document
    
    async def logged_generate(template, context, format):
        print("\n3. GENERANDO DOCUMENTO")
        print(f"   Plantilla: {template.name}")
        print(f"   Secciones a generar: {template.sections}")
        print(f"   Formato destino: {format.value if format else template.format.value}")
        
        # Generar secciones con log
        print("\n   Generando secciones:")
        document = await original_generate(template, context, format)
        
        for section in document.sections:
            print(f"   - Sección '{section.title}': {len(section.content)} caracteres")
        
        print(f"\n   Documento generado: {document.id}")
        print(f"   Total de secciones: {len(document.sections)}")
        return document
    
    doc_service.generator.generate_document = logged_generate
    
    # 4. Sobreescribir método de formateo
    original_format = doc_service.format_handler.format_document
    
    def logged_format(document, output_format, style_config=None):
        print("\n4. FORMATEANDO DOCUMENTO")
        print(f"   Formato solicitado: {output_format.value}")
        print(f"   Estilo aplicado: {style_config['css_framework'] if style_config else 'default'}")
        
        formatted = original_format(document, output_format, style_config)
        print(f"   Documento formateado: {len(formatted)} caracteres")
        return formatted
    
    doc_service.format_handler.format_document = logged_format
    
    # 5. Sobreescribir método de almacenamiento
    original_save = doc_service.storage.save_document
    
    async def logged_save(document):
        print("\n5. ALMACENANDO DOCUMENTO")
        print(f"   ID del documento: {document.id}")
        print(f"   Formato a guardar: {document.format.value}")
        print(f"   Directorio destino: {doc_service.storage.dirs[document.format]}")
        
        result = await original_save(document)
        print(f"   Documento guardado exitosamente")
        return result
    
    doc_service.storage.save_document = logged_save
    
    # Ejecutar generación de reporte
    try:
        result = await doc_service.generate_project_report(
            project_data=project_data,
            template_id="project_summary",
            style="default",
            output_format="html"
        )
        
        print("\n6. PROCESO COMPLETADO")
        print(f"   ID del documento: {result['document_id']}")
        print(f"   Ruta del archivo: {result['file_path']}")
        print(f"   Formato generado: {result['format']}")
        print("\n=== FIN DE LA VERIFICACIÓN DEL FLUJO ===")
        
        # Verificaciones
        assert result["format"] == "html"
        assert "file_path" in result
        assert "document_id" in result
        
        # Verificar que el archivo existe y no está vacío
        file_path = Path(result["file_path"])
        assert file_path.exists(), f"El archivo {file_path} no existe"
        assert file_path.stat().st_size > 0, f"El archivo {file_path} está vacío"
        
        return result
        
    finally:
        # Restaurar métodos originales
        doc_service._build_documentation_context = original_build_context
        doc_service.generator.generate_document = original_generate
        doc_service.format_handler.format_document = original_format
        doc_service.storage.save_document = original_save

async def test_create_physical_files():
    """Test para verificar explícitamente la creación de archivos físicos"""
    # 1. Configurar componentes
    vector_store = MockVectorStore()
    orchestrator = MockOrchestrator()
    base_dir = Path("./test_explicit_files")
    
    # Limpiar y crear directorio de prueba
    if base_dir.exists():
        for file in base_dir.glob("**/*"):
            if file.is_file():
                file.unlink()
    else:
        base_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Crear servicio
    storage = DocumentStorage(base_dir=base_dir)
    format_handler = FormatHandler()
    template_manager = TemplateStyleManager()
    generator = DocumentGenerator(orchestrator.llm)
    
    service = DocumentationService(
        vector_store=vector_store,
        rag_orchestrator=orchestrator,
        base_dir=base_dir
    )
    service.storage = storage
    service.generator = generator 
    service.format_handler = format_handler
    service.template_manager = template_manager
    
    # 3. Crear documento básico
    document = Document(
        id=f"explicit_test_{datetime.utcnow().timestamp()}",
        type=DocumentType.REPORT,
        title="Informe de Prueba Explícito",
        sections=[
            DocumentSection(
                title="Sección de Prueba",
                content="Este es un contenido de prueba para verificar la creación de archivos.",
                order=0
            )
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        format=DocumentFormat.MARKDOWN,
        metadata={"test": True}
    )
    
    # 4. Generar contenido y guardar en archivos
    formats_to_test = [
        DocumentFormat.MARKDOWN, 
        DocumentFormat.HTML, 
        DocumentFormat.JSON
    ]
    
    print("\n===== TEST DE CREACIÓN DE ARCHIVOS =====")
    for format_type in formats_to_test:
        # Cambiar formato del documento
        document.format = format_type
        
        # Generar contenido según formato
        content = format_handler.format_document(document, format_type)
        print(f"\nGenerado contenido para {format_type.value}: {len(content)} bytes")
        
        # Guardar manualmente en archivo
        file_path = storage._save_file(document, content)
        print(f"Guardado en: {file_path}")
        
        # Verificar existencia y contenido del archivo
        assert file_path.exists(), f"El archivo {file_path} no existe"
        file_size = file_path.stat().st_size
        assert file_size > 0, f"El archivo {file_path} está vacío (0 bytes)"
        
        print(f"Verificado: archivo existe con {file_size} bytes")
        
        # Leer contenido para verificar
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            assert document.title in file_content, f"El título no se encontró en el contenido"
        
        print(f"Verificado: contenido correcto en el archivo")
    
    print("\n===== TEST COMPLETADO CON ÉXITO =====")

    if __name__ == "__main__":

        # Ejecutar tests manualmente
        asyncio.run(test_document_format_conversion(FormatHandler()))
                
        # Crear service para pruebas
        vector_store = MockVectorStore()
        orchestrator = MockOrchestrator()
        storage = DocumentStorage(base_dir=Path("./test_docs"))
        service = DocumentationService(vector_store, orchestrator, Path("./test_docs"))
        service.storage = storage

        # Ejecutar pruebas de generación y conversión
        asyncio.run(test_generate_report_with_format_choice(service))
        asyncio.run(test_convert_existing_document(service))

        # Ejecutar prueba de verificación de flujo
        test_service = doc_service()
        asyncio.run(test_detailed_report_flow(test_service))