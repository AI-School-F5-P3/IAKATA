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
│   │   │   ├── doc.py            # Endpoints de documentación
│   │   │   ├── monitor.py        # Endpoints de monitorización
│   │   │   └── analysis.py       # Endpoints de análisis
│   │   └── middleware/
│   │       └── error_handler.py
│   │
│   ├── orchestrator/              # Módulo RAG Orchestrator
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # Lógica de orquestación
│   │   └── chat.py               # Gestión de chat
│   │
│   ├── retriever/                 # Módulo Retriever
│   │   ├── __init__.py
│   │   ├── search.py             # Motor de búsqueda
│   │   ├── rank.py               # Motor de ranking
│   │   └── filter.py             # Sistema de filtrado
│   │
│   ├── llm/                       # Módulo LLM
│   │   ├── __init__.py
│   │   ├── gpt.py                # Integración GPT-4
│   │   ├── temperature.py        # Control de temperatura
│   │   └── validator.py          # Validaciones
│   │
│   ├── knowledge/                 # Knowledge Sources Manager
│   │   ├── __init__.py
│   │   ├── pdf_processor.py      # Procesamiento PDFs
│   │   ├── db_reader.py          # Lectura BD
│   │   └── source_manager.py     # Gestión fuentes
│   │
│   ├── vectorstore/              # Index & Vector Store
│   │   ├── __init__.py
│   │   ├── tokenizer.py          # Tokenización
│   │   ├── normalizer.py         # Normalización
│   │   ├── embeddings.py         # Generación embeddings
│   │   └── index_manager.py      # Gestión índices
│   │
│   ├── documentation/            # Sistema Documentación
│   │   ├── __init__.py
│   │   ├── generator.py          # Generación docs
│   │   ├── templates.py          # Gestión plantillas
│   │   └── learning_store.py     # Almacén aprendizaje
│   │
│   ├── monitoring/               # Sistema Monitorización
│   │   ├── __init__.py
│   │   ├── status.py            # Estado sistema
│   │   ├── metrics.py           # Métricas
│   │   └── alerts.py            # Alertas
│   │
│   ├── analysis/                 # Sistema Análisis
│   │   ├── __init__.py
│   │   ├── kpi.py               # Análisis KPIs
│   │   ├── advisor.py           # Recomendaciones
│   │   └── feedback.py          # Sistema feedback
│   │
│   ├── config/                   # Configuraciones
│   │   ├── __init__.py
│   │   ├── settings.py          # Config general
│   │   └── logging.py           # Config logs
│   │
│   └── utils/                    # Utilidades
│       ├── __init__.py
│       ├── db.py                # Utils BD
│       └── helpers.py           # Utils generales
│
├── tests/                        # Tests
│   ├── __init__.py
│   ├── test_api/
│   ├── test_orchestrator/
│   ├── test_retriever/
│   ├── test_llm/
│   ├── test_knowledge/
│   ├── test_vectorstore/
│   ├── test_documentation/
│   ├── test_monitoring/
│   └── test_analysis/
│
├── docs/                         # Documentación
│   ├── api/
│   ├── architecture/
│   └── deployment/
│
└── logs/                        # Archivos de log
    ├── api/
    ├── app/
    ├── error/
    └── audit/
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
