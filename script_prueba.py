# simple_doc_test.py
from pathlib import Path
from datetime import datetime
import json
import os

# Crear directorios para formatos
output_dir = Path("./simple_docs")
output_dir.mkdir(exist_ok=True)

formats = ["markdown", "html", "json", "pdf", "excel"]
for fmt in formats:
    (output_dir / fmt).mkdir(exist_ok=True)

# Datos de ejemplo
document_data = {
    "id": f"test_{datetime.now().timestamp()}",
    "title": "Documento de Prueba",
    "sections": [
        {
            "title": "Sección 1: Introducción",
            "content": "Este es el contenido de la primera sección.\n\n* Punto 1\n* Punto 2\n* Punto 3",
            "order": 0
        },
        {
            "title": "Sección 2: Metodología",
            "content": "Metodología aplicada en el proyecto.\n\n1. Paso uno\n2. Paso dos\n3. Paso tres",
            "order": 1
        }
    ],
    "metadata": {
        "author": "Script de prueba",
        "date": datetime.now().isoformat()
    }
}

print("\n===== GENERANDO DOCUMENTOS DE PRUEBA =====")

# Función para generar contenido según el formato
def generate_content(doc_format):
    if doc_format == "markdown":
        content = [f"# {document_data['title']}\n"]
        content.append(f"*Generado el {document_data['metadata']['date']}*\n")
        
        for section in sorted(document_data['sections'], key=lambda s: s['order']):
            content.append(f"\n## {section['title']}\n")
            content.append(section['content'])
            content.append("\n")
        
        return "\n".join(content)
    
    elif doc_format == "html":
        content = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{document_data['title']}</title>",
            "<style>body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }</style>",
            "</head>",
            "<body>",
            f"<h1>{document_data['title']}</h1>"
        ]
        
        for section in sorted(document_data['sections'], key=lambda s: s['order']):
            content.append(f"<section>")
            content.append(f"<h2>{section['title']}</h2>")
            content.append(f"<div>{section['content'].replace('\n\n', '<br><br>').replace('*', '•')}</div>")
            content.append("</section>")
        
        content.append("</body></html>")
        return "\n".join(content)
    
    elif doc_format == "json":
        return json.dumps(document_data, indent=2, default=str)
    
    elif doc_format == "pdf":
        # Simulamos contenido para PDF (en realidad LaTeX que podría convertirse a PDF)
        content = [
            r"\documentclass{article}",
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage{geometry}",
            r"\geometry{margin=2.5cm}",
            f"\\title{{{document_data['title']}}}",
            r"\begin{document}",
            r"\maketitle"
        ]
        
        for section in sorted(document_data['sections'], key=lambda s: s['order']):
            content.append(f"\\section{{{section['title']}}}")
            content.append(section['content'].replace('*', r'$\bullet$'))
        
        content.append(r"\end{document}")
        return "\n".join(content)
    
    elif doc_format == "excel":
        # Simulamos una estructura JSON que podría convertirse a Excel
        return json.dumps({
            "metadata": {
                "title": document_data['title'],
                "created_at": document_data['metadata']['date'],
                "sheet_name": "Documento"
            },
            "sections": document_data['sections']
        }, indent=2, default=str)

# Generar archivos para cada formato
files_created = []
for doc_format in formats:
    try:
        # Generar contenido según formato
        content = generate_content(doc_format)
        
        # Determinar extensión
        extensions = {
            "markdown": ".md", 
            "html": ".html", 
            "json": ".json",
            "pdf": ".pdf", 
            "excel": ".xlsx"
        }
        
        # Crear nombre y ruta del archivo
        file_name = f"test_{doc_format}_{int(datetime.now().timestamp())}{extensions[doc_format]}"
        file_path = output_dir / doc_format / file_name
        
        # Guardar archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Verificar tamaño
        size = file_path.stat().st_size
        print(f"✓ Documento {doc_format}: guardado en {file_path} ({size} bytes)")
        files_created.append((doc_format, file_path))
        
    except Exception as e:
        print(f"✗ Error generando documento {doc_format}: {str(e)}")

# Imprimir resumen
print(f"\nTotal de formatos: {len(formats)}")
print(f"Archivos creados: {len(files_created)}")
print(f"Directorio: {output_dir.absolute()}")

print("\n===== DOCUMENTOS GENERADOS =====")
for doc_format, path in files_created:
    print(f"- {doc_format}: {path.name}")