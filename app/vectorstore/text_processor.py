from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import re
import logging
from .chunk_manager import ChunkManager
from .common_types import TextType, ProcessedText, Chunk

logger = logging.getLogger(__name__)

class TextType(Enum):
    """Tipos de texto que se pueden procesar."""
    MAIN_CONTENT = "main_content"
    EXAMPLE = "example"
    PROCEDURE = "procedure"
    CONCEPT = "concept"
    DEFINITION = "definition"

@dataclass
class ProcessedText:
    """Representa un texto procesado con sus metadatos."""
    text: str
    text_type: TextType
    metadata: Dict[str, Any]
    section_id: str

class TextProcessor:
    """Procesa y prepara textos para vectorización, incluyendo chunking."""
    
    def __init__(self, 
                 chunk_size: int = 512,
                 chunk_overlap: int = 50):
        """
        Inicializa el procesador de texto con chunking.
        
        Args:
            chunk_size: Tamaño objetivo de chunks en tokens
            chunk_overlap: Solapamiento entre chunks en tokens
        """
        # Inicializar ChunkManager
        self.chunk_manager = ChunkManager(
            target_chunk_size=chunk_size,
            overlap_size=chunk_overlap
        )
        
        # Precompilar expresiones regulares
        self._patterns_to_remove = [
            re.compile(r'©.*?reservados', re.IGNORECASE | re.DOTALL),
            re.compile(r'ÍNDICE.*?PARTE', re.IGNORECASE | re.DOTALL),
            re.compile(r'ISBN.*?\d+', re.IGNORECASE | re.DOTALL)
        ]
        
        # Términos clave para extracción de frases
        self._kata_terms = {
            'kata de mejora', 'kata de coaching', 'lean kata', 'toyota kata',
            'coaching kata', 'kata principal', 'ciclo pdca', 'gestión visual',
            'a3 thinking', '5s', 'kanban', 'value stream mapping', 'jidoka',
            'just-in-time', 'tps', 'sistema de producción toyota', 'mejora continua',
            'kaizen', 'gemba walks', 'rutinas de coaching', 'experimentos rápidos',
            'análisis de causa raíz', 'gestión del cambio', 'estandarización',
            'práctica deliberada', 'estado actual', 'estado objetivo', 'condición objetivo',
            'situación actual', 'situación objetivo', 'reto', 'target state'
        }

    def clean_text(self, text: str) -> str:
        """
        Limpieza mejorada del texto manteniendo la integridad de las oraciones.
        """
        try:
            if not text:
                return ""

            # 1. Aplicar patrones de limpieza básicos
            for pattern in self._patterns_to_remove:
                text = pattern.sub('', text)

            # 2. Normalizar espacios y saltos de línea
            text = re.sub(r'\s+', ' ', text)
            
            # 3. Arreglar puntuación cortada
            text = re.sub(r'\s+([.,;:!?])', r'\1', text)
            
            # 4. Normalizar guiones y símbolos
            text = text.replace('—', '-').replace('--', '-')
            text = text.replace('»', '').replace('«', '')
            
            # 5. Eliminar caracteres sueltos al inicio
            text = re.sub(r'^[^a-zA-Z0-9\s]{1,2}\s*', '', text)
            
            # 6. Arreglar espacios alrededor de paréntesis
            text = re.sub(r'\(\s+', '(', text)
            text = re.sub(r'\s+\)', ')', text)
            
            # 7. Asegurar que el texto comienza con letra o número
            text = re.sub(r'^[^a-zA-Z0-9]+', '', text)
            
            # 8. Eliminar espacios al inicio y final
            text = text.strip()
            
            # 9. Asegurar que tenemos una oración completa
            if text and not text[-1] in '.!?':
                text += '.'
                
            return text

        except Exception as e:
            logger.error(f"Error en clean_text: {e}")
            return text.strip()

    def process_section(self, section: Dict[str, Any]) -> List[ProcessedText]:
        """
        Procesa una sección completa del documento y genera chunks.
        
        Args:
            section: Diccionario con datos de la sección
            
        Returns:
            Lista de textos procesados (cada uno potencialmente dividido en chunks)
        """
        processed_texts = []
        section_id = str(section.get('page_range', [0, 0])[0])

        try:
            # Procesar texto principal
            if 'content' in section and 'full_text' in section['content']:
                main_text = self.clean_text(section['content']['full_text'])
                
                processed_text = ProcessedText(
                    text=main_text,
                    text_type=TextType.MAIN_CONTENT,
                    metadata={
                        'title': section.get('title', ''),
                        'category': section.get('primary_category', ''),
                        'relevance': section.get('relevance', {}).get('level', '')
                    },
                    section_id=section_id
                )
                
                # Generar chunks para el texto principal
                chunks = self.chunk_manager.create_chunks(processed_text)
                processed_texts.extend(self._convert_chunks_to_processed_texts(chunks))

            # Procesar ejemplos
            if 'content' in section and 'examples' in section['content']:
                for example in section['content']['examples']:
                    cleaned_text = self.clean_text(example)
                    example_text = ProcessedText(
                        text=cleaned_text,
                        text_type=TextType.EXAMPLE,
                        metadata={'type': 'example'},
                        section_id=section_id
                    )
                    
                    # Generar chunks para el ejemplo
                    chunks = self.chunk_manager.create_chunks(example_text)
                    processed_texts.extend(self._convert_chunks_to_processed_texts(chunks))

            # Procesar procedimientos
            if 'content' in section and 'procedures' in section['content']:
                for procedure in section['content']['procedures']:
                    cleaned_text = self.clean_text(procedure)
                    procedure_text = ProcessedText(
                        text=cleaned_text,
                        text_type=TextType.PROCEDURE,
                        metadata={'type': 'procedure'},
                        section_id=section_id
                    )
                    
                    # Generar chunks para el procedimiento
                    chunks = self.chunk_manager.create_chunks(procedure_text)
                    processed_texts.extend(self._convert_chunks_to_processed_texts(chunks))

            return processed_texts

        except Exception as e:
            logger.error(f"Error procesando sección: {str(e)}")
            return []

    def _convert_chunks_to_processed_texts(self, chunks: List[Chunk]) -> List[ProcessedText]:
        """
        Convierte chunks en ProcessedText manteniendo metadata y relaciones.
        
        Args:
            chunks: Lista de chunks generados
            
        Returns:
            Lista de ProcessedText con información de chunks
        """
        processed_chunks = []
        
        for chunk in chunks:
            # Enriquecer metadata con información del chunk
            enhanced_metadata = {
                **chunk.metadata,
                'chunk_info': {
                    'start_idx': chunk.start_idx,
                    'end_idx': chunk.end_idx,
                    'tokens': chunk.tokens,
                    'chunk_id': chunk.chunk_id,
                    'overlap_prev': chunk.overlap_prev,
                    'overlap_next': chunk.overlap_next
                }
            }
            
            processed_chunks.append(ProcessedText(
                text=chunk.text,
                text_type=TextType(chunk.metadata['text_type']),
                metadata=enhanced_metadata,
                section_id=chunk.section_id
            ))
            
        return processed_chunks

    def extract_key_phrases(self, text: str) -> List[str]:
        """
        Extrae frases clave relacionadas con Lean Kata.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de frases clave encontradas
        """
        phrases = []
        text_lower = text.lower()
        
        for term in self._kata_terms:
            if term in text_lower:
                # Obtener contexto alrededor del término
                start = max(0, text_lower.find(term) - 50)
                end = min(len(text), text_lower.find(term) + len(term) + 50)
                
                # Ajustar a límites de oraciones
                context = text[start:end].strip()
                if start > 0:
                    sentence_start = text.rfind('.', 0, start)
                    if sentence_start != -1:
                        start = sentence_start + 1
                sentence_end = text.find('.', end)
                if sentence_end != -1:
                    end = sentence_end + 1
                
                context = text[start:end].strip()
                phrases.append(context)
        
        return phrases

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas del procesamiento de texto y chunking.
        
        Returns:
            Diccionario con estadísticas
        """
        chunk_stats = self.chunk_manager.get_stats()
        return {
            'chunk_settings': chunk_stats,
            'kata_terms_count': len(self._kata_terms),
            'patterns_count': len(self._patterns_to_remove)
        }