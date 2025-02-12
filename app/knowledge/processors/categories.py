from enum import Enum
from typing import List, Dict

class LeanKataCategory(Enum):
    PROCESS = "process"
    TRIBE = "tribe"
    CHALLENGE = "challenge"
    ACTUAL_STATE = "actual_state"
    TARGET_STATE = "target_state"
    OBSTACLE = "obstacle"
    HYPOTHESIS = "hypothesis"
    EXPERIMENT = "experiment"
    TASK = "task"
    RESULT = "result"
    LEARNING = "learning"
    MENTAL_CONTRAST = "mental_contrast"
    METHODOLOGY = "methodology"
    GENERAL = "general"

# Palabras clave asociadas a cada categoría
CATEGORY_KEYWORDS = {
    LeanKataCategory.PROCESS: ["proceso", "flujo de trabajo", "procedimiento", "método"],
    LeanKataCategory.TRIBE: ["equipo", "tribu", "grupo", "miembros"],
    LeanKataCategory.CHALLENGE: ["reto", "desafío", "objetivo", "meta"],
    LeanKataCategory.ACTUAL_STATE: ["estado actual", "situación actual", "condición actual"],
    LeanKataCategory.TARGET_STATE: ["estado objetivo", "estado meta", "condición deseada"],
    LeanKataCategory.OBSTACLE: ["obstáculo", "impedimento", "barrera", "dificultad"],
    LeanKataCategory.HYPOTHESIS: ["hipótesis", "suposición", "teoría"],
    LeanKataCategory.EXPERIMENT: ["experimento", "prueba", "ensayo", "test"],
    LeanKataCategory.TASK: ["tarea", "actividad", "paso", "acción"],
    LeanKataCategory.RESULT: ["resultado", "consecuencia", "efecto"],
    LeanKataCategory.LEARNING: ["aprendizaje", "lección", "conocimiento adquirido"],
    LeanKataCategory.MENTAL_CONTRAST: ["contraste mental", "evaluación", "valoración"],
    LeanKataCategory.METHODOLOGY: ["metodología", "kata", "rutina", "práctica"],
}

def get_text_categories(text: str) -> List[LeanKataCategory]:
    """
    Identifica las categorías presentes en un texto dado
    """
    text = text.lower()
    categories = set()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            categories.add(category)
    
    return list(categories) if categories else [LeanKataCategory.GENERAL]