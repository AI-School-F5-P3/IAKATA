from typing import Dict, Any, Optional, List
import json
from pathlib import Path
import logging
from dataclasses import asdict
from .text_processor import ProcessedText, TextType

logger = logging.getLogger(__name__)

class MetadataManager:
    """
    Gestiona los metadatos asociados a los textos vectorizados.
    Mantiene la relación entre IDs y contenido original.
    """
    
    def __init__(self):
        self.metadata = {}
        self.id_counter = 0
        self.section_mapping = {}  # Mapeo de secciones a IDs
        
    def generate_id(self, processed_text: ProcessedText) -> str:
        """
        Genera un ID único para un texto procesado
        """
        text_id = f"{processed_text.section_id}_{processed_text.text_type.value}_{self.id_counter}"
        self.id_counter += 1
        return text_id
        
    def add_entry(self, processed_text: ProcessedText) -> str:
        """
        Añade una entrada de metadatos usando el ID original
        """
        try:
            # Generar ID manteniendo el formato original
            text_id = f"{processed_text.section_id}_{processed_text.text_type.value}_{self.id_counter}"
            
            # Guardar metadatos
            self.metadata[text_id] = {
                'text': processed_text.text,
                'type': processed_text.text_type.value,
                'metadata': processed_text.metadata,
                'section_id': processed_text.section_id
            }
            
            # Actualizar mapeo de secciones
            if processed_text.section_id not in self.section_mapping:
                self.section_mapping[processed_text.section_id] = []
            self.section_mapping[processed_text.section_id].append(text_id)
            
            self.id_counter += 1
            return text_id
                
        except Exception as e:
            logger.error(f"Error al añadir entrada de metadatos: {str(e)}")
            raise

    def get_entry(self, text_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera los metadatos para un ID dado
        """
        entry = self.metadata.get(text_id)
        if entry is None:
            logger.debug(f"Metadata no encontrada para ID {text_id}. IDs disponibles: {list(self.metadata.keys())}")
        return entry
        
    def get_section_entries(self, section_id: str) -> List[Dict[str, Any]]:
        """
        Recupera todos los textos asociados a una sección
        
        Args:
            section_id: ID de la sección
            
        Returns:
            Lista de metadatos de los textos en la sección
        """
        text_ids = self.section_mapping.get(section_id, [])
        return [self.metadata[text_id] for text_id in text_ids if text_id in self.metadata]
        
    def update_entry(self, text_id: str, updates: Dict[str, Any]) -> bool:
        """
        Actualiza los metadatos de una entrada existente
        
        Args:
            text_id: ID del texto a actualizar
            updates: Diccionario con los campos a actualizar
            
        Returns:
            bool indicando éxito
        """
        if text_id not in self.metadata:
            return False
            
        try:
            self.metadata[text_id].update(updates)
            return True
        except Exception as e:
            logger.error(f"Error al actualizar metadatos: {str(e)}")
            return False
            
    def delete_entry(self, text_id: str) -> bool:
        """
        Elimina una entrada de metadatos
        
        Args:
            text_id: ID del texto a eliminar
            
        Returns:
            bool indicando éxito
        """
        if text_id not in self.metadata:
            return False
            
        try:
            # Eliminar de metadata
            section_id = self.metadata[text_id]['section_id']
            del self.metadata[text_id]
            
            # Eliminar de section_mapping
            if section_id in self.section_mapping:
                self.section_mapping[section_id].remove(text_id)
                
            return True
        except Exception as e:
            logger.error(f"Error al eliminar entrada: {str(e)}")
            return False
            
    def save(self, directory: Path):
        """
        Guarda los metadatos en archivos JSON
        
        Args:
            directory: Directorio donde guardar los archivos
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            
            # Guardar metadata principal
            metadata_file = directory / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                
            # Guardar mapeo de secciones
            mapping_file = directory / "section_mapping.json"
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.section_mapping, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Metadatos guardados en {directory}")
            
        except Exception as e:
            logger.error(f"Error al guardar metadatos: {str(e)}")
            raise
            
    def load(self, directory: Path):
        """
        Carga metadatos desde archivos JSON
        
        Args:
            directory: Directorio donde están los archivos
        """
        try:
            # Cargar metadata principal
            metadata_file = directory / "metadata.json"
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
                
            # Cargar mapeo de secciones
            mapping_file = directory / "section_mapping.json"
            with open(mapping_file, 'r', encoding='utf-8') as f:
                self.section_mapping = json.load(f)
                
            # Actualizar contador de IDs
            if self.metadata:
                max_id = max(int(text_id.split('_')[-1]) for text_id in self.metadata.keys())
                self.id_counter = max_id + 1
                
            logger.info(f"Metadatos cargados desde {directory}")
            
        except Exception as e:
            logger.error(f"Error al cargar metadatos: {str(e)}")
            raise
            
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas sobre los metadatos almacenados
        """
        stats = {
            'total_entries': len(self.metadata),
            'total_sections': len(self.section_mapping),
            'entries_by_type': {},
            'average_text_length': 0
        }
        
        # Contar entradas por tipo
        for entry in self.metadata.values():
            entry_type = entry['type']
            stats['entries_by_type'][entry_type] = stats['entries_by_type'].get(entry_type, 0) + 1
            
        # Calcular longitud media de textos
        if self.metadata:
            total_length = sum(len(entry['text']) for entry in self.metadata.values())
            stats['average_text_length'] = total_length / len(self.metadata)
            
        return stats
    def save_with_id(self, text_id: str, processed_text: ProcessedText) -> None:
        """
        Guarda metadata usando un ID específico
        Args:
            text_id: ID a usar
            processed_text: Texto procesado con metadata
        """
        try:
            # Guardar metadata
            self.metadata[text_id] = {
                'text': processed_text.text,
                'type': processed_text.text_type.value,
                'metadata': processed_text.metadata,
                'section_id': processed_text.section_id
            }
            
            # Actualizar mapeo de secciones
            if processed_text.section_id not in self.section_mapping:
                self.section_mapping[processed_text.section_id] = []
            if text_id not in self.section_mapping[processed_text.section_id]:
                self.section_mapping[processed_text.section_id].append(text_id)
                
        except Exception as e:
            logger.error(f"Error guardando metadata para ID {text_id}: {e}")
            raise