# IAKATA - Asistente Inteligente para LeanKata

La aplicación IAKATA es un sistema de asistencia basado en la metodología LeanKata que utiliza tecnología RAG (Retrieval-Augmented Generation) y LLMs (Modelos de Lenguaje de Aprendizaje Profundo) para ayudar a los usuarios a implementar procesos de mejora continua en sus organizaciones. El sistema se integra con la aplicación LK-WEB a través de una API REST, permitiendo a los usuarios completar "tableros" LeanKata con información de calidad, recibir validaciones y sugerencias en tiempo real, y mantener una base de conocimiento de todos los proyectos de mejora acometidos. El asistente chatbot guía a los usuarios a través de la metodología, ayudándoles a definir retos, estados objetivo, obstáculos, experimentos, y a documentar resultados y aprendizajes, facilitando así la resolución de problemas en equipos multidisciplinares de manera estructurada.

## Índice

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Módulos Principales](#módulos-principales)
- [API](#api)
- [Contribución](#contribución)

## Características

- **Integración con LK-WEB**: Se conecta con la aplicación LK-WEB mediante API REST para proporcionar asistencia inteligente.
- **RAG (Retrieval-Augmented Generation)**: Combina la búsqueda de información relevante con la generación de respuestas contextualizadas.
- **Asistencia en tiempo real**: Proporciona validaciones y sugerencias mientras los usuarios completan los tableros LeanKata.
- **Base de conocimiento**: Mantiene y accede a una base de conocimiento compartida sobre proyectos de mejora.
- **Procesamiento en lenguaje natural**: Entiende consultas en español relacionadas con la metodología LeanKata.
- **Chatbot interactivo**: Permite a los usuarios hacer preguntas sobre la metodología o recibir ayuda específica.
- **Generación de documentación**: Crea documentación automática de proyectos para facilitar la transferencia de conocimiento.

## Arquitectura

IAKATA sigue una arquitectura modular basada en los siguientes componentes:

1. **API REST**: Interfaz de comunicación con LK-WEB.
2. **Knowledge Sources Manager**: Gestiona las fuentes de conocimiento (documentos, BD).
3. **Index & Vector Store**: Procesa e indexa la información para búsqueda eficiente.
4. **Retriever**: Recupera información relevante basada en consultas.
5. **RAG Orchestrator**: Coordina el flujo entre recuperación de información y generación de respuestas.
6. **LLM**: Módulo de interacción con GPT-4o-mini para la generación de respuestas.
7. **Chat Manager**: Gestiona las conversaciones con los usuarios.
8. **Documentation Generator**: Genera documentación automática de proyectos.

## Requisitos

- Python 3.11.9
- Acceso a la API de OpenAI
- Base de datos LK-WEB (para integración)

## Instalación

### Usando pip

```bash
# Clonar el repositorio
git clone https://github.com/AI-School-F5-P3/iakata.git
cd iakata

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Create the file .env located in the folder "IAKATA"
# Copy the information placed on ´.env_example´ and fill it with your personal data
```

## Uso

### Iniciar la API

```bash
# Modo desarrollo
uvicorn app.main:app --reload

# Modo producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Probar el chatbot localmente

```bash
python -m app.test_chat_4
```

## Estructura del Proyecto

```
PROYECTO_IAKATA/
│
├── IAKATA/
│   ├── .devcontainer/
│   ├── .pytest_cache/
│   ├── app/
│   │   ├── documentation/
│   │   ├── front/
│   │   ├── knowledge/
│   │   ├── llm/
│   │   ├── models/
│   │   ├── monitoring/
│   │   ├── orchestrator/
│   │   ├── retriever/
│   │   ├── utils/
│   │   ├── vectorstore/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── test_chat_2.py
│   │   ├── test_chat_3.py
│   │   ├── test_chat_4.py
│   │   └── test_vector_store.py
│   │
│   ├── cache/
│   ├── docs/
│   │   └── architecture/
│   │       ├── complete_modules.mermaid
│   │       ├── flow-diagram-spaced.mermaid
│   │       ├── medium.mermaid
│   │       ├── project-structure.md
│   │       └── simple.mermaid
│   │
│   ├── logs/
│   ├── test/
│   ├── tests/
│   ├── __init__.py
│   ├── .dockerignore
│   ├── .env
│   ├── .gitignore
│   ├── docker-compose.yml
│   ├── docker-compose.yml.backup
│   ├── Dockerfile
│   └── Dockerfile.fastapi
│
├── OUTLINE/
├── TIMELINE/
├── MYSQL/
└── SONARQUBE ISSUE LOCATIONS/
```

## Módulos Principales

### Knowledge Sources Manager

Gestiona y actualiza toda la información relevante que se utilizará en el proceso de búsqueda y generación de respuestas, incluyendo conexión con repositorios (documentos PDF, base de datos LK-WEB) y mecanismos de ingesta de datos.

### Retriever

Localiza y prioriza la información relevante en la base de conocimiento, en respuesta a las consultas de los usuarios o de la aplicación LK-WEB, utilizando búsqueda semántica, ranking y filtrado de resultados.

### RAG Orchestrator

Coordina la comunicación entre el Módulo de Recuperación, el LLM y la capa de negocio de LK-WEB, gestionando el contexto, ensamblando prompts y procesando respuestas.

### LLM (GPT-4)

Provee respuestas, sugerencias y orientación basadas en la información contextual recibida y el conocimiento general del modelo, con control de temperatura para ajustar el estilo según las necesidades.

### Chat Manager

Administra la interacción conversacional del usuario con el sistema, manteniendo el estado de la conversación y permitiendo un diálogo continuo y coherente.

## API

IAKATA expone los siguientes endpoints principales:

- `/board/ai`: Para validar y mejorar secciones del tablero
- `/chatbot`: Para interactuar con el asistente mediante chat
- `/doc`: Para la generación de documentación

Consulta la documentación completa de la API en `/docs` cuando el servidor esté en ejecución.

## Contribución

1. Fork el repositorio
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios
4. Ejecuta los tests (`pytest`)
5. Haz commit de tus cambios (`git commit -m 'Añade nueva funcionalidad'`)
6. Push a la rama (`git push origin feature/nueva-funcionalidad`)
7. Abre un Pull Request


