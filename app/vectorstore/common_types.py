from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

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
    overlap_prev: str = None
    overlap_next: str = None