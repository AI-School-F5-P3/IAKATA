# Estructura del Proyecto IAKATA

Esta documentación detalla la estructura de carpetas del proyecto IAKATA y el propósito de cada componente.

## Estructura General

```plaintext
iakata/
│
├── Dockerfile                      # Configuración de contenedor Docker
├── docker-compose.yml             # Configuración de servicios Docker
├── requirements.txt               # Dependencias del proyecto
├── README.md                      # Documentación principal
├── .gitignore                     # Archivos ignorados por git
├── .env                          # Variables de entorno (no versionado)
│
├── app/                           # Código principal de la aplicación
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada de la aplicación
│   │
│   ├── api/                       # Capa API REST
│   │   ├── __init__.py
│   │   ├── routes/                # Endpoints de la API
│   │   │   ├── __init__.py
│   │   │   ├── chat.py           # Endpoints de chat
│   │   │   ├── board.py          # Endpoints de tableros
│   │   │   └── monitor.py        # Endpoints de monitorización
│   │   ├── models.py             # Modelos de datos Pydantic
│   │   ├── services/             # Servicios de la API
│   │   │   ├── __init__.py
│   │   │   └── rag_services.py   # Servicios RAG
│   │   └── middleware/           # Middleware de la API
│   │       └── error_handler.py  # Manejo de errores
│   │
│   ├── chat/                      # Módulo de Chat
│   │   ├── __init__.py
│   │   ├── manager.py            # Gestión de chat
│   │   ├── session.py            # Manejo de sesiones
│   │   ├── types.py              # Tipos de datos
│   │   └── exceptions.py         # Excepciones específicas
│   │
│   ├── orchestrator/              # Módulo RAG Orchestrator
│   │   ├── __init__.py
│   │   └── orchestrator.py       # Orquestación de componentes
│   │
│   ├── retriever/                 # Módulo Retriever
│   │   ├── __init__.py
│   │   ├── retriever.py          # Sistema principal
│   │   ├── search.py             # Motor de búsqueda
│   │   ├── rank.py               # Motor de ranking
│   │   ├── filter.py             # Sistema de filtrado
│   │   └── types.py              # Tipos de datos
│   │
│   ├── llm/                       # Módulo LLM
│   │   ├── __init__.py
│   │   ├── gpt.py                # Integración GPT-4
│   │   ├── temperature.py        # Control de temperatura
│   │   ├── validator.py          # Validaciones
│   │   └── types.py              # Tipos de datos
│   │
│   ├── knowledge/                 # Knowledge Sources Manager
│   │   ├── __init__.py
│   │   ├── processors/           # Procesadores de datos
│   │   │   ├── __init__.py
│   │   │   ├── pdf_processor.py  # Procesamiento PDFs
│   │   │   ├── categories.py     # Categorización
│   │   │   └── structure_analyzer.py # Análisis estructural
│   │   └── processed/            # Datos procesados
│   │       └── books/            # Libros procesados
│   │
│   ├── vectorstore/              # Index & Vector Store
│   │   ├── __init__.py
│   │   ├── processed/
│   │   │   └── vectors/         # Vectores generados
│   │   ├── vector_store.py       # Almacén principal
│   │   ├── vectorizer.py         # Generación de embeddings
│   │   ├── text_processor.py     # Procesamiento de texto
│   │   ├── chunk_manager.py      # Gestión de chunks
│   │   ├── cache_manager.py      # Gestión de caché
│   │   ├── metadata_manager.py   # Gestión de metadatos
│   │   ├── quality_validator.py  # Validación de calidad
│   │   ├── retry_manager.py      # Gestión de reintentos
│   │   └── common_types.py       # Tipos comunes
│   │
│   └── config/                   # Configuraciones
│       ├── __init__.py
│       ├── settings.py           # Config general
│       └── logging.py            # Config logs
│
├── tests/                        # Tests
│   ├── __init__.py
│   ├── test_api/
│   ├── test_chat/
│   ├── test_orchestrator/
│   ├── test_retriever/
│   ├── test_llm/
│   └── test_vectorstore/
│
├── docs/                         # Documentación
│   ├── api/                      # Docs de la API
│   ├── architecture/             # Docs de arquitectura
│   └── deployment/               # Docs de despliegue
│
└── logs/                        # Archivos de log
    ├── api/                     # Logs de API
    ├── app/                     # Logs de aplicación
    └── error/                   # Logs de errores
```

## Notas Importantes

1. Todos los módulos principales están en la carpeta `app/`
2. Cada módulo tiene su propio `__init__.py` para gestión de imports
3. La estructura sigue una organización modular para facilitar el desarrollo y mantenimiento
4. Los logs están separados por tipo para mejor organización
5. La documentación está organizada por áreas

## Convenciones de Nombrado

- Archivos y carpetas en minúsculas con guiones bajos
- Módulos Python con nombres descriptivos y concisos
- Tests con prefijo `test_`
- Logs organizados por categoría

## Sistema de Logs

- Los logs de aplicación se guardan en `logs/`
- Cada componente tiene su propia carpeta de logs
- Los archivos de log no se incluyen en git (usar .gitignore)
- Se mantienen los directorios vacíos con .gitkeep
