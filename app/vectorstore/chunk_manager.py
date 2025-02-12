from typing import List, Dict, Any, Optional, Tuple
import re
from dataclasses import dataclass
import nltk
from nltk.tokenize import sent_tokenize
import logging
from common_types import TextType, ProcessedText, Chunk
import tiktoken

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    """Representa un chunk de texto procesado."""
    text: str
    start_idx: int
    end_idx: int
    tokens: int
    metadata: Dict[str, Any]
    section_id: str
    chunk_id: str
    overlap_prev: Optional[str] = None
    overlap_next: Optional[str] = None

class ChunkManager:
    """Gestiona la creación y procesamiento de chunks manteniendo coherencia semántica."""
    
    def __init__(
        self,
        target_chunk_size: int = 512,
        overlap_size: int = 50,
        min_chunk_size: int = 100,
        max_chunk_size: int = 1000,
        model_name: str = "gpt-4o-mini"
    ):
        """
        Inicializa el gestor de chunks.
        
        Args:
            target_chunk_size: Tamaño objetivo en tokens
            overlap_size: Tamaño del solapamiento en tokens
            min_chunk_size: Tamaño mínimo permitido para un chunk
            max_chunk_size: Tamaño máximo permitido para un chunk
            model_name: Nombre del modelo para el tokenizer
        """
        try:
            nltk.download('punkt', quiet=True)
            self.tokenizer = tiktoken.encoding_for_model(model_name)
            
            self.target_chunk_size = target_chunk_size
            self.overlap_size = overlap_size
            self.min_chunk_size = min_chunk_size
            self.max_chunk_size = max_chunk_size
            
            # Patrones para detectar límites semánticos
            self.boundary_patterns = [
                r'\n\n',              # Párrafos
                r'\.\s+[A-Z]',        # Oraciones
                r';\s+[A-Z]',         # Punto y coma
                r':\s+[A-Z]',         # Dos puntos
                r'\)\s+[A-Z]',        # Paréntesis cerrando
                r'\]\s+[A-Z]',        # Corchete cerrando
            ]
            
            # Keywords que indican coherencia semántica
            self.semantic_keywords = {
                'por ejemplo', 'es decir', 'en otras palabras',
                'sin embargo', 'no obstante', 'por lo tanto',
                'en consecuencia', 'además', 'asimismo',
                'por un lado', 'por otro lado', 'finalmente'
            }
            
            logger.info(
                f"ChunkManager inicializado - Target size: {target_chunk_size}, "
                f"Overlap: {overlap_size}"
            )
            
        except Exception as e:
            logger.error(f"Error inicializando ChunkManager: {str(e)}")
            raise

    def count_tokens(self, text: str) -> int:
        """Cuenta tokens en un texto."""
        return len(self.tokenizer.encode(text))

    def find_semantic_boundary(self, text: str, target_idx: int, direction: str = 'forward') -> int:
        """
        Encuentra el límite semántico más cercano al índice objetivo.
        
        Args:
            text: Texto a analizar
            target_idx: Índice objetivo
            direction: Dirección de búsqueda ('forward' o 'backward')
            
        Returns:
            Índice del límite semántico más apropiado
        """
        try:
            # Definir rango de búsqueda
            search_range = 100  # Ajustar según necesidad
            
            if direction == 'forward':
                search_text = text[target_idx:target_idx + search_range]
                offset = target_idx
            else:
                search_text = text[max(0, target_idx - search_range):target_idx]
                offset = max(0, target_idx - search_range)

            # Buscar patrones de límites
            best_boundary = None
            min_distance = float('inf')
            
            for pattern in self.boundary_patterns:
                matches = list(re.finditer(pattern, search_text))
                
                for match in matches:
                    boundary_idx = match.start() + offset if direction == 'forward' else match.end() + offset
                    distance = abs(boundary_idx - target_idx)
                    
                    if distance < min_distance:
                        # Verificar coherencia semántica
                        if self._check_semantic_coherence(text, boundary_idx):
                            min_distance = distance
                            best_boundary = boundary_idx

            return best_boundary if best_boundary is not None else target_idx
            
        except Exception as e:
            logger.error(f"Error encontrando límite semántico: {str(e)}")
            return target_idx

    def _check_semantic_coherence(self, text: str, boundary_idx: int) -> bool:
        """
        Verifica la coherencia semántica alrededor de un punto de corte.
        
        Args:
            text: Texto completo
            boundary_idx: Índice del límite a verificar
            
        Returns:
            bool indicando si el límite es semánticamente coherente
        """
        try:
            # Obtener contexto alrededor del límite
            context_size = 50
            start = max(0, boundary_idx - context_size)
            end = min(len(text), boundary_idx + context_size)
            context = text[start:end].lower()
            
            # Verificar si hay keywords de cohesión cerca del límite
            for keyword in self.semantic_keywords:
                if keyword in context:
                    # Si el keyword está muy cerca del límite, podría romper la coherencia
                    keyword_pos = context.find(keyword)
                    if abs(keyword_pos - context_size) < 20:
                        return False
                        
            # Verificar balance de estructuras
            opening = sum(1 for c in context[:context_size] if c in '([{')
            closing = sum(1 for c in context[:context_size] if c in ')]}')
            if opening != closing:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error verificando coherencia semántica: {str(e)}")
            return True

    def create_chunks(self, processed_text: ProcessedText) -> List[Chunk]:
        """
        Crea chunks a partir de un texto procesado manteniendo coherencia semántica.
        
        Args:
            processed_text: Texto procesado con metadata
            
        Returns:
            Lista de chunks procesados
        """
        try:
            chunks = []
            text = processed_text.text
            current_idx = 0
            chunk_counter = 0
            
            while current_idx < len(text):
                # Determinar fin del chunk actual
                remaining_text = text[current_idx:]
                target_end = min(
                    len(remaining_text),
                    self._estimate_char_length(self.target_chunk_size)
                )
                
                # Encontrar límite semántico apropiado
                chunk_end = current_idx + self.find_semantic_boundary(
                    text,
                    current_idx + target_end,
                    'forward'
                )
                
                # Extraer chunk y calcular solapamiento
                chunk_text = text[current_idx:chunk_end]
                tokens = self.count_tokens(chunk_text)
                
                # Verificar tamaños mínimo y máximo
                if tokens < self.min_chunk_size and chunks:
                    # Combinar con el chunk anterior si es muy pequeño
                    prev_chunk = chunks[-1]
                    combined_text = prev_chunk.text + chunk_text
                    combined_tokens = self.count_tokens(combined_text)
                    
                    if combined_tokens <= self.max_chunk_size:
                        chunks[-1] = self._create_chunk(
                            combined_text,
                            prev_chunk.start_idx,
                            chunk_end,
                            combined_tokens,
                            processed_text,
                            chunk_counter - 1
                        )
                        current_idx = chunk_end
                        continue
                
                # Crear nuevo chunk
                chunk = self._create_chunk(
                    chunk_text,
                    current_idx,
                    chunk_end,
                    tokens,
                    processed_text,
                    chunk_counter
                )
                
                chunks.append(chunk)
                chunk_counter += 1
                
                # Actualizar índice considerando solapamiento
                if chunk_end - current_idx > self.overlap_size:
                    current_idx = chunk_end - self.overlap_size
                else:
                    current_idx = chunk_end
                    
            # Procesar solapamientos entre chunks
            self._process_overlaps(chunks)
            
            logger.info(
                f"Creados {len(chunks)} chunks a partir de texto de "
                f"{len(text)} caracteres"
            )
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error creando chunks: {str(e)}")
            return []

    def _create_chunk(
        self,
        text: str,
        start_idx: int,
        end_idx: int,
        tokens: int,
        processed_text: ProcessedText,
        chunk_number: int
    ) -> Chunk:
        """Crea un objeto Chunk con la información necesaria."""
        return Chunk(
            text=text,
            start_idx=start_idx,
            end_idx=end_idx,
            tokens=tokens,
            metadata={
                **processed_text.metadata,
                'chunk_number': chunk_number,
                'text_type': processed_text.text_type.value
            },
            section_id=processed_text.section_id,
            chunk_id=f"{processed_text.section_id}_chunk_{chunk_number}"
        )

    def _process_overlaps(self, chunks: List[Chunk]) -> None:
        """Procesa y ajusta los solapamientos entre chunks."""
        for i in range(len(chunks)):
            if i > 0:
                # Solapamiento con chunk anterior
                overlap_text = self._find_overlap(chunks[i-1].text, chunks[i].text)
                chunks[i].overlap_prev = overlap_text
                
            if i < len(chunks) - 1:
                # Solapamiento con chunk siguiente
                overlap_text = self._find_overlap(chunks[i].text, chunks[i+1].text)
                chunks[i].overlap_next = overlap_text

    def _find_overlap(self, text1: str, text2: str) -> Optional[str]:
        """Encuentra el texto solapado entre dos chunks."""
        try:
            # Buscar la subcadena más larga común al final de text1 y principio de text2
            min_overlap = 20  # Caracteres mínimos para considerar solapamiento
            max_overlap = 200  # Caracteres máximos para buscar
            
            for length in range(max_overlap, min_overlap - 1, -1):
                suffix = text1[-length:]
                if text2.startswith(suffix):
                    return suffix
                    
            return None
            
        except Exception as e:
            logger.error(f"Error encontrando solapamiento: {str(e)}")
            return None

    def _estimate_char_length(self, tokens: int) -> int:
        """Estima la longitud en caracteres para un número de tokens."""
        # Aproximación básica: 4 caracteres por token en promedio
        return tokens * 4

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del proceso de chunking."""
        return {
            'target_chunk_size': self.target_chunk_size,
            'overlap_size': self.overlap_size,
            'min_chunk_size': self.min_chunk_size,
            'max_chunk_size': self.max_chunk_size
        }