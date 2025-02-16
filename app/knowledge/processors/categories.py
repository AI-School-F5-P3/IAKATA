from enum import Enum
from typing import List, Dict

class LeanKataCategory(Enum):
    PROCESS = "process"
    TRIBE = "tribe"
    CHALLENGE = "challenge"
    TARGET_STATE = "target_state"
    OBSTACLE = "obstacle"
    HYPOTHESIS = "hypothesis"
    EXPERIMENT = "experiment"
    TASK = "task"
    RESULT = "result"
    LEARNING = "learning"
    METHODOLOGY = "methodology"
    GENERAL = "general"

# Palabras clave para cada categoría
CATEGORY_KEYWORDS = {
    LeanKataCategory.PROCESS: ["proceso", "flujo de trabajo", "procedimiento", "método", "kata de mejora"],
    LeanKataCategory.TRIBE: ["equipo", "tribu", "grupo", "miembros", "kata de coaching"],
    LeanKataCategory.CHALLENGE: ["reto", "desafío", "objetivo", "meta", "challenge"],
    LeanKataCategory.TARGET_STATE: ["estado objetivo", "estado meta", "condición deseada", "target state"],
    LeanKataCategory.OBSTACLE: ["obstáculo", "impedimento", "barrera", "dificultad"],
    LeanKataCategory.HYPOTHESIS: ["hipótesis", "suposición", "teoría", "predicción"],
    LeanKataCategory.EXPERIMENT: ["experimento", "prueba", "ensayo", "test", "pdca"],
    LeanKataCategory.TASK: ["tarea", "actividad", "paso", "acción"],
    LeanKataCategory.RESULT: ["resultado", "consecuencia", "efecto", "medición"],
    LeanKataCategory.LEARNING: ["aprendizaje", "lección", "conocimiento", "hansei"],
    LeanKataCategory.METHODOLOGY: ["metodología", "kata", "rutina", "práctica", "lean kata"],
}

def map_front_category(front_category: str) -> LeanKataCategory:
    """
    Convierte una categoría del front-end al enum LeanKataCategory correspondiente.
    
    Args:
        front_category: String que representa la categoría del front-end
        
    Returns:
        LeanKataCategory correspondiente
    
    Examples:
        >>> map_front_category("challenge")
        LeanKataCategory.CHALLENGE
        >>> map_front_category("targetstate")
        LeanKataCategory.TARGET_STATE
    """
    mapping = {
        "challenge": LeanKataCategory.CHALLENGE,
        "targetstate": LeanKataCategory.TARGET_STATE,
        "obstacle": LeanKataCategory.OBSTACLE,
        "hypothesis": LeanKataCategory.HYPOTHESIS,
        "experiment": LeanKataCategory.EXPERIMENT,
        "task": LeanKataCategory.TASK,
        "result": LeanKataCategory.RESULT,
        "learning": LeanKataCategory.LEARNING,
        "process": LeanKataCategory.PROCESS,
        "tribe": LeanKataCategory.TRIBE,
    }
    normalized_category = front_category.lower().replace(" ", "").replace("-", "")
    return mapping.get(normalized_category, LeanKataCategory.GENERAL)

def get_text_categories(text: str) -> List[LeanKataCategory]:
    """
    Identifica las categorías Lean Kata presentes en un texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Lista de categorías encontradas, o [GENERAL] si no se encuentra ninguna
    """
    text = text.lower()
    categories = set()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            categories.add(category)
    
    return list(categories) if categories else [LeanKataCategory.GENERAL]