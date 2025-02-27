from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path
import logging
import mysql.connector
from mysql.connector import Error
from .types import Document, DocumentFormat

logger = logging.getLogger(__name__)

class DocumentStorage:
    """
    Manejador de almacenamiento de documentos usando MySQL directamente
    """
    
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        base_dir: Optional[Path] = None
    ):
        """
        Inicializa el manejador de almacenamiento
        """
        # Configuración MySQL
        self.db_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        
        # Configurar almacenamiento de archivos
        self.base_dir = base_dir or Path("documents")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear subdirectorios por tipo
        self.dirs = {
            DocumentFormat.MARKDOWN: self.base_dir / "markdown",
            DocumentFormat.HTML: self.base_dir / "html",
            DocumentFormat.JSON: self.base_dir / "json",
            DocumentFormat.PDF: self.base_dir / "pdf"
        }
        for dir_path in self.dirs.values():
            dir_path.mkdir(exist_ok=True)
            
        # Crear tabla si no existe
        self._create_tables()

    def _create_tables(self):
        """Crea las tablas necesarias si no existen"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Crear tabla documentation
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documentation (
                    id VARCHAR(255) PRIMARY KEY,
                    type VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    content TEXT,
                    format VARCHAR(50) NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    doc_metadata JSON,
                    sections JSON
                )
            """)
            
            conn.commit()
            
        except Error as e:
            logger.error(f"Error creando tablas: {e}")
            raise
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    async def save_document(self, document: Document) -> str:
        """
        Guarda un documento en BD y sistema de archivos
        """
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Generar contenido principal
            main_content = self._generate_main_content(document)
            
            # Preparar datos para inserción
            data = {
                'id': document.id,
                'type': document.type.value,
                'title': document.title,
                'content': main_content,
                'format': document.format.value,
                'created_at': document.created_at,
                'updated_at': document.updated_at,
                'doc_metadata': json.dumps(document.metadata),
                'sections': json.dumps([{
                    'title': s.title,
                    'content': s.content,
                    'order': s.order
                } for s in document.sections])
            }
            
            # Insertar en BD
            query = """
                INSERT INTO documentation 
                (id, type, title, content, format, created_at, updated_at, doc_metadata, sections)
                VALUES (%(id)s, %(type)s, %(title)s, %(content)s, %(format)s, 
                        %(created_at)s, %(updated_at)s, %(doc_metadata)s, %(sections)s)
            """
            cursor.execute(query, data)
            conn.commit()
            
            # Guardar archivo
            file_path = self._save_file(document, main_content)
            
            # Actualizar metadata con ruta del archivo
            await self.update_metadata(
                document.id,
                {"file_path": str(file_path)}
            )
            
            return document.id
            
        except Error as e:
            logger.error(f"Error guardando documento: {e}")
            raise
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    async def get_document(self, doc_id: str) -> Optional[Document]:
        """
        Recupera un documento por su ID
        """
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM documentation WHERE id = %s"
            cursor.execute(query, (doc_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
                
            return Document(
                id=result['id'],
                type=result['type'],
                title=result['title'],
                format=DocumentFormat(result['format']),
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                metadata=json.loads(result['doc_metadata']),
                sections=json.loads(result['sections'])
            )
            
        except Error as e:
            logger.error(f"Error recuperando documento: {e}")
            raise
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    async def update_metadata(self, doc_id: str, metadata_updates: Dict[str, Any]) -> bool:
        """
        Actualiza la metadata de un documento
        """
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Obtener metadata actual
            query = "SELECT doc_metadata FROM documentation WHERE id = %s"
            cursor.execute(query, (doc_id,))
            result = cursor.fetchone()
            
            if not result:
                return False
                
            # Actualizar metadata
            current_metadata = json.loads(result['doc_metadata']) if result['doc_metadata'] else {}
            current_metadata.update(metadata_updates)
            
            # Guardar metadata actualizada
            update_query = "UPDATE documentation SET doc_metadata = %s WHERE id = %s"
            cursor.execute(update_query, (json.dumps(current_metadata), doc_id))
            conn.commit()
            
            return True
            
        except Error as e:
            logger.error(f"Error actualizando metadata: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    async def search_documents(
        self,
        query: Optional[str] = None,
        doc_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Document]:
        """
        Busca documentos según criterios
        """
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Construir query base
            base_query = "SELECT * FROM documentation WHERE 1=1"
            params = []
            
            # Añadir filtros
            if query:
                base_query += " AND (title LIKE %s OR content LIKE %s)"
                query_param = f"%{query}%"
                params.extend([query_param, query_param])
                
            if doc_type:
                base_query += " AND type = %s"
                params.append(doc_type)
                
            if start_date:
                base_query += " AND created_at >= %s"
                params.append(start_date)
                
            if end_date:
                base_query += " AND created_at <= %s"
                params.append(end_date)
            
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            
            return [
                Document(
                    id=row['id'],
                    type=row['type'],
                    title=row['title'],
                    format=DocumentFormat(row['format']),
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    metadata=json.loads(row['doc_metadata']),
                    sections=json.loads(row['sections'])
                )
                for row in results
            ]
            
        except Error as e:
            logger.error(f"Error buscando documentos: {e}")
            raise
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def _generate_main_content(self, document: Document) -> str:
        """Genera el contenido principal del documento"""
        if document.format == DocumentFormat.MARKDOWN:
            return self._format_markdown(document)
        elif document.format == DocumentFormat.HTML:
            return self._format_html(document)
        elif document.format == DocumentFormat.JSON:
            return self._format_json(document)
        else:
            raise ValueError(f"Formato no soportado: {document.format}")

    def _format_markdown(self, document: Document) -> str:
        """Formatea documento en Markdown"""
        content = [f"# {document.title}\n"]
        
        if document.metadata:
            content.extend([
                "---",
                "metadata:",
                json.dumps(document.metadata, indent=2),
                "---\n"
            ])
        
        for section in sorted(document.sections, key=lambda s: s.order):
            content.extend([
                f"\n## {section.title}\n",
                section.content,
                "\n"
            ])
            
        return "\n".join(content)

    def _format_html(self, document: Document) -> str:
        """Formatea documento en HTML"""
        content = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{document.title}</title>",
            "</head>",
            "<body>",
            f"<h1>{document.title}</h1>"
        ]
        
        for section in sorted(document.sections, key=lambda s: s.order):
            content.extend([
                f"<section>",
                f"<h2>{section.title}</h2>",
                section.content,
                "</section>"
            ])
            
        content.extend(["</body>", "</html>"])
        return "\n".join(content)

    def _format_json(self, document: Document) -> str:
        """Formatea documento en JSON"""
        return json.dumps({
            "id": document.id,
            "type": document.type.value,
            "title": document.title,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
            "metadata": document.metadata,
            "sections": [{
                "title": section.title,
                "content": section.content,
                "order": section.order
            } for section in sorted(document.sections, key=lambda s: s.order)]
        }, indent=2)

    def _save_file(self, document: Document, content: str) -> Path:
        """Guarda el contenido en un archivo"""
        dir_path = self.dirs[document.format]
        file_name = f"{document.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        extensions = {
            DocumentFormat.MARKDOWN: ".md",
            DocumentFormat.HTML: ".html",
            DocumentFormat.JSON: ".json",
            DocumentFormat.PDF: ".pdf"
        }
        
        file_path = dir_path / f"{file_name}{extensions[document.format]}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return file_path