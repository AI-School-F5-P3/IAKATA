import json
from typing import Dict, List, Set, Optional, Any
from openai import OpenAI
from pathlib import Path
import re
import logging
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeanKataCategory(Enum):
    PROCESS = "Process"
    CHALLENGE = "Challenge"
    ACTUAL_STATE = "ActualState"
    TARGET_STATE = "TargetState"
    OBSTACLE = "Obstacle"
    HYPOTHESIS = "Hypothesis"
    EXPERIMENT = "Experiment"
    RESULTS = "Results"
    LEARNING = "Learning"
    TRIBE = "Tribe"

@dataclass
class LeanKataConcepts:
    METHODOLOGIES = [
        "Ciclo PDCA",
        "Gestión visual",
        "Coaching Kata",
        "Kata de mejora",
        "A3 thinking",
        "5S",
        "Kanban",
        "Value Stream Mapping"
    ]
    
    PRACTICES = [
        "Mejora continua",
        "Gemba walks",
        "Rutinas de coaching",
        "Experimentos rápidos",
        "Análisis de causa raíz",
        "Gestión del cambio",
        "Estandarización"
    ]
    
    TOOLS = [
        "Tableros Lean Kata",
        "Tarjetas de condición objetivo",
        "Formularios A3",
        "Diagramas de espagueti",
        "Matrices de priorización",
        "Indicadores visuales"
    ]
    
    ROLES = [
        "Coach Kata",
        "Aprendiz Kata",
        "Líder de mejora",
        "Facilitador",
        "Equipo de mejora"
    ]

class LeanKataAnalyzer:
    def __init__(self):
        self.concepts = LeanKataConcepts()
        
    def evaluate_relevance(self, content: str, concepts_mentioned: List[str]) -> str:
        """
        Evalúa la relevancia de una sección basada en su contenido y conceptos
        """
        # Patrones que indican alta relevancia
        high_relevance_patterns = [
            r"paso[s]? a paso",
            r"metodología específica",
            r"implementación práctica",
            r"ejemplo[s]? práctico[s]?",
            r"caso[s]? de estudio",
            r"procedimiento[s]?",
            r"técnica[s]? específica[s]?"
        ]
        
        # Contar conceptos clave mencionados
        concept_count = len(concepts_mentioned)
        
        # Verificar patrones de alta relevancia
        has_high_relevance_pattern = any(re.search(pattern, content.lower()) 
                                       for pattern in high_relevance_patterns)
        
        # Determinar relevancia
        if has_high_relevance_pattern and concept_count >= 3:
            return "alta"
        elif concept_count >= 1 or has_high_relevance_pattern:
            return "media"
        return "baja"

    def identify_concepts(self, content: str) -> List[str]:
        """
        Identifica conceptos Lean Kata mencionados en el contenido
        """
        all_concepts = (self.concepts.METHODOLOGIES + 
                       self.concepts.PRACTICES + 
                       self.concepts.TOOLS + 
                       self.concepts.ROLES)
        
        return [concept for concept in all_concepts 
                if concept.lower() in content.lower()]

class StructureAnalyzer:
    system_prompt = """Eres un experto en metodología Lean Kata analizando libros técnicos. Tu misión es identificar y clasificar secciones clave para implementación práctica.

**INSTRUCCIONES CRÍTICAS:**
1. CONTENIDO PRIORITARIO (NO OMITIR):
   - Términos exactos: "Kata de mejora", "Kata de coaching", "Lean Kata", "Toyota Kata"
   - Metodologías: Ciclo PDCA, Gestión visual, A3 thinking
   - Elementos prácticos: Tableros Lean Kata, Rutinas de coaching, Experimentos rápidos

2. PROFUNDIDAD DE ANÁLISIS (POR SECCIÓN):
   - Determinar alcance real (no solo página de mención)
   - Identificar continuidad temática
   - Capturar transiciones entre conceptos

3. CATEGORIZACIÓN PRECISA:
   Usar matriz de decisión:
   ┌────────────────────┬──────────────────────────────┐
   │ Si menciona...      │ Categorizar como...          │
   ├────────────────────┼──────────────────────────────┤
   │ Pasos/metodología   │ Process                      │
   │ Problemas/retos     │ Challenge + Obstacle         │
   │ Datos/resultados    │ Results + Learning           │
   │ Equipos/roles       │ Tribe + Process              │
   └────────────────────┴──────────────────────────────┘

4. CRITERIOS DE RELEVANCIA ESTRICTOS:
   [Alta] Requiere TODOS:
   - Menciona ≥3 conceptos clave
   - Incluye ejemplo/procedimiento
   - Aplica a implementación real

   [Media] ≥2 de:
   - Explica fundamentos teóricos
   - Contextualiza casos de uso
   - Menciona herramientas clave

5. VALIDACIÓN DE DATOS:
   - Verificar coherencia título-contenido
   - Rechazar secciones <0.5 páginas sin conceptos clave
   - Priorizar rangos continuos sobre páginas sueltas

**FORMATO DE SALIDA (JSON ESTRICTO):**
{
  "relevant_sections": [
    {
      "title": "Título exacto (incluir número de capítulo si aplica)",
      "page_range": [int, int] (mínimo 2 páginas por sección),
      "primary_category": "Process/Challenge/ActualState/TargetState/Obstacle/Hypothesis/Experiment/Results/Learning/Tribe",
      "secondary_categories": ["máx 3 categorías de la lista anterior"],
      "relevance": {
        "level": "alta/media/baja",
        "score": 1-10 (10=máxima utilidad práctica)
      },
      "key_concepts": {
        "methodologies": [
            "Ciclo PDCA",
            "Gestión visual",
            "Coaching Kata",
            "otros de la lista proporcionada"
            ],
            "practices": [
            "Mejora continua",
            "otros de la lista proporcionada"
            ],
            "tools": [
            "Tableros Lean Kata",
            "otros de la lista proporcionada"
            ],
            "roles": [
            "Coach Kata",
            "otros de la lista proporcionada"
            ]
        },
        "dependencies": [
            "lista de conceptos prerrequisito"
        ],
        "implementation_utility": {
            "description": "texto explicativo de uso práctico",
            "difficulty": 1-5,
            "prerequisites": [
            "lista de requisitos previos"
            ]
      }
    }
  ]
}

IMPORTANTE: 
- TODOS los campos mostrados son OBLIGATORIOS
- NO omitir ningún campo del formato
- NO añadir campos adicionales
- Mantener EXACTAMENTE la estructura mostrada
- Incluye TODAS las secciones que aporten valor al entendimiento de Lean Kata
- Asegura que cada rango de páginas cubra la sección completa
- Justifica claramente la relevancia de cada sección
- Usar SOLO las categorías y conceptos proporcionados
- La respuesta debe ser ÚNICAMENTE el JSON, sin texto adicional"""

    user_prompt = user_prompt = """Analiza este contenido y genera SOLO secciones relevantes para Lean Kata:

CRITERIOS DE ANÁLISIS:

1. CONTENIDO RELEVANTE:
   A. INCLUIR OBLIGATORIAMENTE secciones que:
      - Describan metodologías Kata
      - Expliquen implementación práctica
      - Contengan pasos o procedimientos
      - Detallen uso de herramientas

   B. INCLUIR SI ES RELEVANTE secciones que:
      - Proporcionen contexto necesario
      - Expliquen conceptos fundamentales
      - Presenten casos de estudio útiles

   C. EXCLUIR SIEMPRE:
      - Prólogos/prefacios/agradecimientos
      - Historia general sin aplicación práctica
      - Contenido no relacionado con Kata/Lean

2. ANÁLISIS DE SECCIONES:
   - Identificar alcance completo (no solo mención inicial)
   - Determinar categorías primarias y secundarias
   - Evaluar relevancia con criterios exactos
   - Extraer conceptos clave por tipo
   - Valorar utilidad de implementación

3. FORMATO DE SALIDA REQUERIDO:
{
    "relevant_sections": [
        {
            "title": "título exacto",
            "page_range": [inicio, fin],
            "primary_category": "categoría principal",
            "secondary_categories": ["otras categorías"],
            "relevance": {
                "level": "alta/media/baja",
                "score": "1-10",
                "justification": "razón específica"
            },
            "key_concepts": {
                "methodologies": ["lista"],
                "practices": ["lista"],
                "tools": ["lista"],
                "roles": ["lista"]
            },
            "implementation_utility": "descripción de aplicabilidad práctica"
        }
    ]
}

CONTENIDO A ANALIZAR:
{input_text}

IMPORTANTE: Devolver SOLO JSON válido, sin texto adicional."""

    

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.kata_analyzer = LeanKataAnalyzer()
        self.valid_categories = [cat.value for cat in LeanKataCategory]
        self.valid_concepts = (self.kata_analyzer.concepts.METHODOLOGIES + 
                             self.kata_analyzer.concepts.PRACTICES + 
                             self.kata_analyzer.concepts.TOOLS + 
                             self.kata_analyzer.concepts.ROLES)
        self.logger = logging.getLogger(__name__)
        # Añadir conceptos críticos para mejorar validación
        self.critical_concepts = {
            'methodologies': [
                'Kata de mejora',
                'Coaching Kata',
                'Ciclo PDCA',
                'Gestión visual'
            ],
            'practices': [
                'Mejora continua',
                'Rutinas de coaching',
                'Experimentos rápidos'
            ],
            'tools': [
                'Tableros Lean Kata',
                'Tarjetas de condición objetivo'
            ]
        }
        
        
    def find_page_ranges(self, text: str, book_content: Dict, current_page: int) -> List[Dict[str, int]]:
        """
        Identifica rangos de páginas más precisos usando análisis de contenido
        """
        ranges = []
        text_lower = text.lower()
        
        # Detectar tipo de sección
        section_types = {
            'kata': 15,      # Secciones de kata necesitan más espacio
            'metodología': 12,
            'capítulo': 10,
            'práctica': 8,
            'ejemplo': 5,
            'default': 3
        }
        
        # Determinar tipo de sección
        section_type = 'default'
        for type_key in section_types.keys():
            if type_key in text_lower:
                section_type = type_key
                break

        # Buscar fin de sección
        end_page = current_page
        min_pages = section_types[section_type]
        
        # Analizar páginas siguientes
        for i in range(current_page + 1, min(current_page + min_pages + 5, len(book_content['pages']))):
            next_page_text = book_content['pages'][i]['text'].lower()
            
            # Detectar fin de sección
            end_markers = [
                'capítulo', 'sección', 'parte',
                'anexo', 'apéndice', 'referencias',
                'conclusión', 'resumen'
            ]
            
            # Si encontramos un marcador de fin, terminamos
            if any(marker in next_page_text for marker in end_markers):
                end_page = i - 1
                break
                
            # Buscar continuidad temática
            section_keywords = self.extract_section_keywords(text)
            if not self.has_thematic_continuity(next_page_text, section_keywords):
                end_page = i - 1
                break
                
            end_page = i

        # Asegurar mínimo de páginas según tipo
        if end_page - current_page < min_pages:
            end_page = min(current_page + min_pages, len(book_content['pages']) - 1)

        ranges.append({
            "start": current_page,
            "end": end_page
        })

        return ranges
    
    def extract_section_content(self, book_content: Dict, start_page: int, end_page: int) -> Dict[str, Any]:
        """
        Extrae y estructura el contenido de una sección manteniendo la coherencia 
        de procedimientos y ejemplos
        """
        content = {
            'full_text': '',
            'key_excerpts': [],
            'examples': [],
            'definitions': [],
            'procedures': []
        }
        
        current_segment = {
            'text': '',
            'type': None
        }
        
        for page_num in range(start_page, end_page + 1):
            page_text = book_content['pages'][page_num]['text']
            
            # 1. Detectar secciones de procedimientos completos
            procedure_markers = [
                'paso[s]?[:]?',
                'procedimiento[:]?',
                '\d+\.\s+[A-Z]'  # Números seguidos de punto y mayúscula
            ]
            
            # 2. Detectar ejemplos completos
            example_markers = [
                'por ejemplo[,:]',
                'ejemplo[,:]',
                'caso práctico'
            ]
            
            paragraphs = page_text.split('\n\n')
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                    
                # Si estamos en medio de un segmento, continuarlo
                if current_segment['type']:
                    if self._is_segment_end(paragraph, current_segment['type']):
                        # Guardar segmento completo
                        if current_segment['type'] == 'procedure':
                            content['procedures'].append(current_segment['text'])
                        elif current_segment['type'] == 'example':
                            content['examples'].append(current_segment['text'])
                        current_segment = {'text': '', 'type': None}
                    else:
                        current_segment['text'] += '\n' + paragraph
                        continue
                
                # Detectar nuevo segmento
                if any(re.search(pattern, paragraph, re.I) for pattern in procedure_markers):
                    current_segment = {
                        'text': paragraph,
                        'type': 'procedure'
                    }
                elif any(re.search(pattern, paragraph, re.I) for pattern in example_markers):
                    current_segment = {
                        'text': paragraph,
                        'type': 'example'
                    }
                else:
                    content['full_text'] += paragraph + '\n\n'
                    
        return content

    def _is_segment_end(self, text: str, segment_type: str) -> bool:
        """Detecta si un párrafo marca el fin de un segmento"""
        if segment_type == 'procedure':
            # Detectar fin de procedimiento
            end_markers = [
                r'\n\s*\d+\.',  # Nuevo número
                r'conclusión',
                r'resumen',
                r'siguiente'
            ]
            return any(re.search(pattern, text, re.I) for pattern in end_markers)
        
        elif segment_type == 'example':
            # Detectar fin de ejemplo
            end_markers = [
                r'\.',  # Punto final
                r'por tanto',
                r'en conclusión'
            ]
            return any(re.search(pattern, text, re.I) for pattern in end_markers)
            
        return False
    
    def create_analysis_prompt(self, sections: List[Dict]) -> str:
        """
        Crea un prompt enriquecido para el análisis con GPT-4
        """
        prompt = "Analiza las siguientes secciones de un libro sobre Lean Kata:\n\n"
        
        for section in sections:
            prompt += f"=== SECCIÓN (Páginas {section['page_range']['start']}-{section['page_range']['end']}) ===\n"
            prompt += f"Título: {section.get('title', 'Sin título')}\n"
            
            # Añadir contenido principal
            if section['content']['full_text']:
                prompt += f"Contenido principal:\n{section['content']['full_text'][:1000]}...\n\n"
            
            # Añadir ejemplos si existen
            if section['content']['examples']:
                prompt += "Ejemplos encontrados:\n"
                for example in section['content']['examples'][:2]:  # Limitamos a 2 ejemplos
                    prompt += f"- {example[:200]}...\n"
            
            # Añadir procedimientos si existen
            if section['content']['procedures']:
                prompt += "Procedimientos encontrados:\n"
                for proc in section['content']['procedures'][:2]:  # Limitamos a 2 procedimientos
                    prompt += f"- {proc[:200]}...\n"
            
            # Añadir definiciones clave si existen
            if section['content']['definitions']:
                prompt += "Definiciones clave:\n"
                for definition in section['content']['definitions'][:2]:
                    prompt += f"- {definition[:200]}...\n"
            
            prompt += "\n---\n\n"
        
        return prompt

    def is_example(self, text: str) -> bool:
        """Identifica si un texto es un ejemplo"""
        example_patterns = [
            r'por ejemplo[,:]',
            r'ejemplo[,:]',
            r'caso práctico',
            r'como ilustración',
            r'veamos un caso'
        ]
        return any(re.search(pattern, text.lower()) for pattern in example_patterns)

    def is_definition(self, text: str) -> bool:
        """Identifica si un texto es una definición"""
        definition_patterns = [
            r'se define como',
            r'significa',
            r'se refiere a',
            r'es un[a]?\s',
            r'consiste en'
        ]
        return any(re.search(pattern, text.lower()) for pattern in definition_patterns)

    def is_procedure(self, text: str) -> bool:
        """Identifica si un texto describe un procedimiento"""
        # Patrones específicos de Lean Kata
        kata_procedure_patterns = [
            r'kata de mejora[:]?\s+(?:\d+\.|paso|primero)',
            r'kata de coaching[:]?\s+(?:\d+\.|paso|primero)',
            r'rutina[s]? de (?:mejora|coaching)[:]?\s+(?:\d+\.|paso|primero)',
            r'ciclo pdca[:]?\s+(?:\d+\.|paso|primero)',
            r'implementación de kata[:]?\s+(?:\d+\.|paso|primero)',
            r'método[s]? de (?:mejora|coaching)[:]?\s+(?:\d+\.|paso|primero)'
        ]
        
        # Si encontramos un patrón específico de Kata, es alta prioridad
        if any(re.search(pattern, text.lower()) for pattern in kata_procedure_patterns):
            return True
        
        # Patrones generales de procedimientos
        general_patterns = [
            r'paso[s]?[:]?\s+(?:\d+\.|primero)',
            r'procedimiento[:]?\s+(?:\d+\.|primero)',
            r'método[:]?\s+(?:\d+\.|primero)',
            r'(?:1|primero)[.,]\s+[A-Z]'  # Inicio de enumeración
        ]
        
        # Verificar que el texto tiene estructura de procedimiento
        has_general_pattern = any(re.search(pattern, text.lower()) for pattern in general_patterns)
        
        if has_general_pattern:
            # Verificar que tiene múltiples pasos
            steps = re.findall(r'\d+\.|\b(?:primero|segundo|tercero)\b', text.lower())
            return len(steps) > 1
            
        return False

    def is_key_excerpt(self, text: str) -> bool:
        """Identifica si un texto es un extracto clave"""
        # Buscar menciones de conceptos importantes
        key_concepts = [
            'kata', 'lean', 'toyota', 'mejora continua',
            'coaching', 'experimento', 'objetivo', 'estado actual',
            'estado objetivo', 'condición objetivo'
        ]
        
        text_lower = text.lower()
        concept_count = sum(1 for concept in key_concepts if concept in text_lower)
        
        # Considerar extracto clave si menciona al menos 2 conceptos
        return concept_count >= 2

    def extract_section_keywords(self, text: str) -> Set[str]:
        """
        Extrae palabras clave que definen la temática de la sección
        """
        text_lower = text.lower()
        keywords = set()
        
        # Palabras clave de Lean Kata
        lean_kata_terms = {
            'kata', 'lean', 'toyota', 'mejora', 'proceso',
            'coaching', 'experimento', 'objetivo', 'estado',
            'condición', 'rutina', 'práctica'
        }
        
        # Extraer términos relevantes
        words = set(text_lower.split())
        keywords.update(words & lean_kata_terms)
        
        # Detectar frases compuestas
        phrases = {
            'mejora continua', 'estado actual', 'estado objetivo',
            'kata de mejora', 'kata de coaching'
        }
        
        for phrase in phrases:
            if phrase in text_lower:
                keywords.add(phrase)
                
        return keywords

    def has_thematic_continuity(self, text: str, keywords: Set[str]) -> bool:
        """
        Verifica si un texto mantiene continuidad temática con las palabras clave
        """
        text_lower = text.lower()
        
        # Contar coincidencias de palabras clave
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        
        # Requiere al menos 2 coincidencias para considerar continuidad
        return matches >= 2

    def process_section(self, section: Dict) -> Dict:
        """Procesa y valida una sección individual, completando campos faltantes"""
        # Campos básicos requeridos
        if 'title' not in section or 'page_range' not in section:
            raise ValueError("Faltan campos básicos obligatorios")

        # Validar y corregir page_range
        if not isinstance(section['page_range'], list) or len(section['page_range']) != 2:
            raise ValueError("Formato inválido de page_range")

        # Asegurar y completar categorías
        if 'primary_category' not in section:
            section['primary_category'] = 'Process'  # Categoría por defecto
        if 'secondary_categories' not in section:
            section['secondary_categories'] = []

        # Procesar relevance
        section['relevance'] = self.process_relevance(section.get('relevance', {}))

        # Procesar key_concepts
        section['key_concepts'] = self.process_key_concepts(section.get('key_concepts', {}))

        # Procesar implementation_utility
        section['implementation_utility'] = self.process_implementation_utility(
            section.get('implementation_utility', {})
        )

        # Asegurar dependencies
        if 'dependencies' not in section:
            section['dependencies'] = []

        return section

    def process_relevance(self, relevance: Dict) -> Dict:
        """Procesa y completa la información de relevancia"""
        if not isinstance(relevance, dict):
            relevance = {}

        default_relevance = {
            'level': 'media',
            'score': 5,
            'justification': 'No especificada'
        }

        return {**default_relevance, **relevance}

    def process_key_concepts(self, concepts: Dict) -> Dict:
        """Procesa y completa los conceptos clave"""
        if not isinstance(concepts, dict):
            concepts = {}

        default_concepts = {
            'methodologies': [],
            'practices': [],
            'tools': [],
            'roles': []
        }

        return {**default_concepts, **concepts}

    def process_implementation_utility(self, utility: Dict) -> Dict:
        """Procesa y completa la información de utilidad de implementación"""
        if not isinstance(utility, dict):
            utility = {}

        default_utility = {
            'description': 'No especificada',
            'difficulty': 3,
            'prerequisites': []
        }

        return {**default_utility, **utility}
        
    
    
    def validate_section_content(self, section: Dict) -> bool:
        """
    Validación mejorada que verifica la coherencia entre contenido y conceptos
    con mayor flexibilidad
        """
        try:
            # Verificar coherencia entre título y conceptos
            title = section.get('title', '').lower()
            justification = section.get('justification', '')
           
            if not title:
                logger.warning("Título vacío")
                return False

            # Si falta justificación, generarla basada en el título
            if not justification:
                logger.info(f"Generando justificación para: {title}")
                section['justification'] = f"Sección relevante para Lean Kata relacionada con {title}"
            
            # Ampliar patrones de validación
            kata_patterns = {
                'mejora': ['Kata de mejora', 'Mejora continua', 'Ciclo PDCA'],
                'coaching': ['Coaching Kata', 'Rutinas de coaching'],
                'gestión visual': ['Gestión visual', 'Tableros Lean Kata'],
                'a3': ['A3 thinking'],
                'gemba': ['Gemba walks'],
                'experimentos': ['Experimentos rápidos'],
                'análisis': ['Análisis de causa raíz'],
                'estandarización': ['Estandarización'],
                'lean': ['Mejora continua', 'Kata de mejora'],
                'toyota': ['Toyota Kata', 'Sistema Toyota'],
                'proceso': ['Procesos', 'Flujo de valor'],
                'reto': ['Kata de mejora', 'Experimentos rápidos'],
                'objetivo': ['Tarjetas de condición objetivo', 'Gestión visual'],
                'aprendizaje': ['Aprendizaje organizacional', 'Desarrollo de habilidades'],
                'personas': ['Coach Kata', 'Aprendiz Kata'],
                'equipo': ['Líder de mejora', 'Equipo de mejora'],
                'metodología': ['Kata de mejora', 'Coaching Kata'],
                'desarrollo': ['Mejora continua', 'Rutinas de coaching'],
                'cambio': ['Gestión del cambio', 'Mejora continua'],
                        }
            
            # Verificar que los conceptos asignados tienen sentido con el contenido
            content_text = f"{title} {justification}"
            relevant_concepts = []
            for pattern, concepts in kata_patterns.items():
                if pattern in content_text:
                    relevant_concepts.extend(concepts)
                    
                if relevant_concepts:
                    section['key_concepts'] = list(set(relevant_concepts))
                    return True
            
            # Ampliar indicadores de Lean Kata
            lean_indicators = [
                'lean', 'toyota', 'kata', 'mejora continua', 
                'proceso', 'mejora', 'coaching', 'gestión visual',
                'experimento', 'aprendizaje', 'desarrollo', 'habilidades',
                'herramienta', 'eficiencia', 'calidad', 'productividad', 'implementación',
                'mindset', 'hábitos', 'mentalidad', 'transformación', 'cultura', 'equipo', 'personas',
                'método'
            ]
            
            # Si no hay conceptos específicos, verificar indicadores generales
            if not relevant_concepts:
                if any(indicator in title_lower or indicator in justification_lower 
                    for indicator in lean_indicators):
                    logger.info(f"Sección con indicadores generales de Lean: {section['title']}")
                    return True
                else:
                    logger.warning(f"No se encontraron conceptos relevantes para: {section['title']}")
                    return False
            
            # Actualizar conceptos
            section['key_concepts'] = list(set(relevant_concepts) & set(self.valid_concepts))
            
            return True

        except KeyError as e:
            logger.error(f"Campo requerido faltante en validación de contenido: {e}")
            return False

    def evaluate_contextual_relevance(self, section: Dict) -> bool:
        """Evalúa la relevancia contextual de una sección"""
        context_patterns = {
            'fundamentos': ['Comprender los principios básicos', 'Base conceptual'],
            'desarrollo': ['Desarrollo de personas', 'Crecimiento personal'],
            'transformación': ['Cambio cultural', 'Transformación organizacional'],
            'metodología': ['Forma de trabajo', 'Método de mejora']
        }
        
        content = f"{section['title'].lower()} {section['justification'].lower()}"
        
        for context, phrases in context_patterns.items():
            if any(phrase.lower() in content for phrase in phrases):
                if 'key_concepts' not in section or not section['key_concepts']:
                    section['key_concepts'] = ['Mejora continua', 'Kata de mejora']
                return True
                
        return False
    
    def is_potential_section_start(self, text: str) -> bool:
        """
        Identifica si un texto puede ser el inicio de una sección relevante
        """
        # Patrones de inicio de sección
        section_patterns = [
            r'capítulo\s+[\dIVXLC]+',
            r'parte\s+[\dIVXLC]+',
            r'sección\s+[\dIVXLC]+',
            r'kata\s+de',
            r'metodología\s+',
            r'escalón\s+\d+',
            r'anexo\s+[\dIVXLC]+'
        ]
        
        text_lower = text.lower()
        
        # Verificar patrones
        if any(re.search(pattern, text_lower) for pattern in section_patterns):
            return True
            
        # Verificar conceptos clave en primeras líneas
        first_lines = '\n'.join(text.split('\n')[:3]).lower()
        key_concepts = ['kata', 'lean', 'toyota', 'mejora continua', 'coaching']
        
        return any(concept in first_lines for concept in key_concepts)


    def validate_page_range(self, section: Dict) -> bool:
        try:
            # Tu código actual...
            
            # Añadir validación de contexto
            if not self.validate_range_context(section):
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error validando rango: {str(e)}")
            return False
    
    def validate_section(self, section: Dict) -> bool:
        """
        Valida que una sección tenga todos los campos requeridos y sean válidos
        """
        required_fields = {
            'title': str,
            'page_range': list,
            'primary_category': str,
            'secondary_categories': list,
            'relevance': dict,
            'key_concepts': dict
        }
        
        try:
            # Validar campos requeridos y tipos
            for field, field_type in required_fields.items():
                if field not in section:
                    self.logger.warning(f"Campo requerido faltante: {field}")
                    return False
                if not isinstance(section[field], field_type):
                    self.logger.warning(f"Tipo inválido para {field}: {type(section[field])}")
                    return False
                    
            # Validar estructura de relevance
            if not all(k in section['relevance'] for k in ['level', 'score']):
                self.logger.warning("Estructura de relevance incompleta")
                return False
                
            # Validar estructura de key_concepts
            required_concept_types = ['methodologies', 'practices', 'tools', 'roles']
            if not all(k in section['key_concepts'] for k in required_concept_types):
                self.logger.warning("Estructura de key_concepts incompleta")
                return False
            
            # Validación más flexible para secciones críticas
            if self.is_critical_section(section):
                # Si es una sección crítica pero no tiene conceptos, los añadimos
                if 'key_concepts' not in section:
                    section['key_concepts'] = {}
                if 'methodologies' not in section['key_concepts']:
                    section['key_concepts']['methodologies'] = []
                
                # Asegurar que tenga al menos un concepto Kata
                if not any(concept in section['key_concepts']['methodologies'] 
                        for concept in ['Kata de mejora', 'Coaching Kata']):
                    section['key_concepts']['methodologies'].append('Kata de mejora')
                    self.logger.info(f"Añadido concepto Kata a sección crítica: {section['title']}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error en validación de sección: {str(e)}")
            return False

    def validate_range_context(self, section: Dict) -> bool:
        """Valida el rango en contexto del contenido"""
        start, end = section['page_range']
        title = section.get('title', '').lower()
        
        # Validar coherencia con el tipo de contenido
        if 'introducción' in title and (end - start) > 10:
            logger.warning("Rango sospechoso para introducción")
            return False
            
        if 'kata' in title and (end - start) < 2:
            logger.warning("Rango insuficiente para concepto core")
            return False
            
        # Validar contra estructura del libro
        if not self.is_range_within_chapter(section):
            return False
            
        return True
    
    def is_critical_section(self, section: Dict) -> bool:
        """
        Determina si una sección es crítica para Lean Kata
        """
        title_lower = section['title'].lower()
        
        critical_keywords = ['kata', 'lean', 'toyota', 'mejora continua', 'coaching']
        
        if any(keyword in title_lower for keyword in critical_keywords):
            return True
            
        for concept_type, concepts in self.critical_concepts.items():
            section_concepts = section.get('key_concepts', {}).get(concept_type, [])
            if any(concept in concepts for concept in section_concepts):
                return True
                
        return False

    def enrich_critical_section(self, section: Dict) -> Dict:
        """
        Enriquece una sección crítica con conceptos adicionales
        """
        if not self.is_critical_section(section):
            return section
        
        # Asegurar que existen todas las estructuras necesarias
        if 'key_concepts' not in section:
            section['key_concepts'] = {}
        
        # Añadir todas las categorías requeridas si no existen
        for category in ['methodologies', 'practices', 'tools', 'roles']:
            if category not in section['key_concepts']:
                section['key_concepts'][category] = []
        
        # Añadir conceptos críticos usando el diccionario critical_concepts
        for concept_type, critical_concepts in self.critical_concepts.items():
            if not section['key_concepts'][concept_type]:  # Si la lista está vacía
                section['key_concepts'][concept_type].append(critical_concepts[0])
        
        # Asegurar que tiene relevancia alta
        if 'relevance' not in section:
            section['relevance'] = {}
        section['relevance']['level'] = 'alta'
        section['relevance']['score'] = 9
        
        return section

    def is_range_within_chapter(self, section: Dict) -> bool:
        """Verifica que el rango no cruce límites de capítulos"""
        # Implementación pendiente - requiere metadata del libro
        return True

    def validate_categories(self, section: Dict) -> bool:
        """
        Validación específica de categorías
        """
        try:
            # Validar categoría primaria
            if section['primary_category'] not in self.valid_categories:
                logger.warning(f"Categoría primaria inválida: {section['primary_category']}")
                return False

            # Validar y limpiar categorías secundarias
            valid_secondary_cats = [cat for cat in section['secondary_categories'] 
                                if cat in self.valid_categories]
            
            # Asegurar que las categorías secundarias son diferentes de la primaria
            valid_secondary_cats = [cat for cat in valid_secondary_cats 
                                if cat != section['primary_category']]
            
            # Actualizar las categorías secundarias
            section['secondary_categories'] = valid_secondary_cats

            # Validar que la combinación de categorías tiene sentido
            category_groups = {
                'Process': ['Challenge', 'Experiment', 'Learning'],
                'Challenge': ['Process', 'TargetState', 'Obstacle'],
                'ActualState': ['TargetState', 'Obstacle', 'Process'],
                'TargetState': ['ActualState', 'Challenge', 'Experiment'],
                'Obstacle': ['Hypothesis', 'Experiment', 'Challenge'],
                'Hypothesis': ['Experiment', 'Results', 'Obstacle'],
                'Experiment': ['Results', 'Learning', 'Hypothesis'],
                'Results': ['Learning', 'Experiment', 'Hypothesis'],
                'Learning': ['Process', 'Results', 'Experiment'],
                'Tribe': ['Process', 'Challenge', 'Learning']
            }

            # Verificar que las categorías secundarias son compatibles con la primaria
            compatible_categories = category_groups.get(section['primary_category'], [])
            section['secondary_categories'] = [cat for cat in valid_secondary_cats 
                                            if cat in compatible_categories]

            return True

        except KeyError as e:
            logger.error(f"Campo requerido faltante en validación de categorías: {e}")
            return False
            
    def extract_json_safely(self, text: str) -> Optional[Dict]:
        """
        Extrae y valida JSON de la respuesta de forma segura
        """
        try:
            # Eliminar cualquier texto antes o después del JSON
            json_pattern = r'(\{[\s\S]*\})'
            matches = re.findall(json_pattern, text)
            
            if not matches:
                self.logger.error("No se encontró estructura JSON en la respuesta")
                return None
                
            # Tomar el JSON más largo encontrado (probablemente el más completo)
            json_str = max(matches, key=len)
            
            # Limpiar el JSON
            json_str = json_str.strip()
            json_str = re.sub(r'[\n\r\t]', ' ', json_str)
            json_str = re.sub(r'\s+', ' ', json_str)
            
            # Intentar parsear el JSON
            return json.loads(json_str)
            
        except Exception as e:
            self.logger.error(f"Error procesando JSON: {str(e)}")
            self.logger.debug(f"Texto problemático: {text[:500]}...")
            return None
                                

    def analyze_book_structure(self, book_content: Dict) -> Dict:
        try:
            analyzed_sections = []
            
            # Buscar secciones de procedimientos primero
            for i, page in enumerate(book_content['pages']):
                page_text = page['text']
                
                # Asegurar que cada sección tenga una categoría por defecto
                if "metadata" in page and "category" not in page["metadata"]:
                    page["metadata"]["category"] = "default"
                    logger.warning(f"Falta 'category' en la sección de la página {i}. Asignando 'default'.")
                    
                # Priorizar secciones que contengan procedimientos Kata
                if any(keyword in page_text.lower() for keyword in 
                    ['kata de mejora', 'kata de coaching', 'rutina de mejora', 'ciclo pdca']):
                    
                    ranges = self.find_page_ranges(
                        text=page_text,
                        book_content=book_content,
                        current_page=i
                    )
                    
                    if ranges:
                        section_content = self.extract_section_content(
                            book_content,
                            ranges[0]['start'],
                            ranges[0]['end']
                        )
                        
                        if section_content['procedures']:  # Si encontramos procedimientos
                            analyzed_sections.append({
                                'page_range': ranges[0],
                                'content': section_content,
                                'title': self.extract_section_title(page_text),
                                'priority': 'high'
                            })
            

            # Preparar contenido para análisis GPT
            analysis_content = self.create_analysis_prompt(analyzed_sections)
            
            # Realizar análisis con GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self.user_prompt + "\n\nContenido a analizar:\n" + analysis_content}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Procesar respuesta
            structure_analysis = self.extract_json_safely(response.choices[0].message.content)
            
            if not structure_analysis:
                return {"error": "No se pudo extraer JSON válido"}
            
            # Enriquecer y validar secciones
            if 'relevant_sections' in structure_analysis:
                valid_sections = []
                for i, section in enumerate(structure_analysis['relevant_sections']):
                    if i < len(analyzed_sections):
                        section['content'] = analyzed_sections[i]['content']
                    
                    if self.validate_section(section):
                        if self.is_critical_section(section):
                            section = self.enrich_critical_section(section)
                        valid_sections.append(section)
                        logger.info(f"Sección procesada: {section['title']}")
                    else:
                        logger.warning(f"Sección inválida: {section['title']}")
                
                structure_analysis['relevant_sections'] = valid_sections
            
            return structure_analysis
            
        except Exception as e:
            logger.error(f"Error en el análisis de estructura: {str(e)}")
            return {"error": str(e)}

    def extract_section_title(self, text: str) -> str:
        """
        Extrae el título de una sección del texto
        """
        # Buscar patrones comunes de títulos
        title_patterns = [
            r'(?:capítulo|parte|sección)\s+[\dIVXLC]+[.:]\s*([^\n]+)',
            r'(?:kata|metodología)\s+de\s+([^\n]+)',
            r'escalón\s+\d+[.:]\s*([^\n]+)',
            r'anexo\s+[\dIVXLC]+[.:]\s*([^\n]+)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        # Si no se encuentra un patrón específico, tomar la primera línea no vacía
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return lines[0] if lines else "Sección sin título"
                                
    def analyze_books_structure(self, extraction_file: Path) -> Dict:
        """
        Analiza la estructura de todos los libros en el archivo de extracción
        """
        try:
            with open(extraction_file, 'r', encoding='utf-8') as f:
                extraction_data = json.load(f)

            analysis_results = {
                "books_analysis": [],
                "total_tokens_used": 0,
                "errors": []
            }

            for book in extraction_data['books']:
                try:
                    logger.info(f"\nAnalizando estructura de: {book['filename']}")
                    book_analysis = self.analyze_book_structure(book)
                    
                    if isinstance(book_analysis, dict) and "error" in book_analysis:
                        analysis_results["errors"].append({
                            "filename": book['filename'],
                            "error": book_analysis["error"]
                        })
                        continue
                    
                    analysis_results['books_analysis'].append({
                        "filename": book['filename'],
                        "analysis": book_analysis
                    })
                except Exception as e:
                    logger.error(f"Error procesando {book['filename']}: {str(e)}")
                    analysis_results["errors"].append({
                        "filename": book['filename'],
                        "error": str(e)
                    })

            return analysis_results

        except Exception as e:
            logger.error(f"Error en el análisis de libros: {str(e)}")
            return {"error": str(e)}
    
    

def save_structure_analysis(analysis_results: Dict, output_dir: Path):
    """Guarda los resultados del análisis de estructura"""
    try:
        output_file = output_dir / "structure_analysis.json"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Análisis guardado en: {output_file}")
        return output_file
    
    except Exception as e:
        logger.error(f"Error al guardar el análisis: {str(e)}")
        raise