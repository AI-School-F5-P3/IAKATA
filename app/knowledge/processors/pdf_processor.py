import fitz  # PyMuPDF
from typing import Dict, List
from pathlib import Path
import tiktoken
import re

class PDFProcessor:
    def __init__(self):
        """Inicializa el procesador"""
        pass

    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Cuenta tokens usando el tokenizer de GPT"""
        encoder = tiktoken.encoding_for_model(model)
        return len(encoder.encode(text))

    def clean_text(self, text: str) -> str:
        """Limpieza básica del texto"""
        # Eliminar múltiples espacios en blanco
        text = re.sub(r'\s+', ' ', text)
        # Eliminar múltiples saltos de línea
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Procesa un PDF y retorna su contenido estructurado
        """
        doc = fitz.open(pdf_path)
        content = {
            'filename': Path(pdf_path).name,
            'total_pages': len(doc),
            'pages': [],
            'total_tokens': 0,
            'total_characters': 0
        }

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            cleaned_text = self.clean_text(text)

            if cleaned_text:
                tokens = self.count_tokens(cleaned_text)
                page_content = {
                    'page_number': page_num + 1,
                    'text': cleaned_text,
                    'tokens': tokens,
                    'characters': len(cleaned_text)
                }
                
                content['pages'].append(page_content)
                content['total_tokens'] += tokens
                content['total_characters'] += len(cleaned_text)

        return content

    def analyze_books(self, pdf_paths: List[str]) -> Dict:
        """
        Analiza múltiples libros y proporciona estadísticas básicas
        """
        analysis = {
            'books': [],
            'total_tokens': 0,
            'total_characters': 0,
            'estimated_cost': 0
        }

        for pdf_path in pdf_paths:
            book_content = self.process_pdf(pdf_path)
            analysis['books'].append(book_content)
            analysis['total_tokens'] += book_content['total_tokens']
            analysis['total_characters'] += book_content['total_characters']

        # Calcular costo estimado (usando tarifa de gpt-3.5-turbo)
        analysis['estimated_cost'] = (analysis['total_tokens'] / 1000) * 0.001

        return analysis