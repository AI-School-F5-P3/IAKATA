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
│   │   │   └── monitor.py        # Endpoints de monitorización
│   │   └── middleware/            # Middleware de la API
│   │       └── error_handler.py   # Manejo de errores
│   │
│   ├── core/                      # Sistema RAG principal
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # Orquestador RAG
│   │   ├── llm.py                # Integración con GPT-4
│   │   ├── retriever.py          # Sistema de recuperación
│   │   └── chat.py               # Lógica de chat
│   │
│   ├── knowledge/                 # Gestión de fuentes de conocimiento
│   │   ├── __init__.py
│   │   ├── pdf_processor.py      # Procesamiento de PDFs
│   │   ├── db_reader.py          # Lectura de base de datos
│   │   └── source_manager.py     # Gestión de fuentes
│   │
│   ├── vectorstore/              # Sistema de vectorización e indexación
│   │   ├── __init__.py
│   │   ├── tokenizer.py          # Tokenización de texto
│   │   ├── normalizer.py         # Normalización de texto
│   │   ├── embeddings.py         # Generación de embeddings
│   │   └── index_manager.py      # Gestión de índices vectoriales
│   │
│   ├── documentation/            # Sistema de documentación
│   │   ├── __init__.py
│   │   ├── generator.py          # Generación de documentos
│   │   ├── templates.py          # Plantillas de documentación
│   │   └── learning_store.py     # Almacenamiento de aprendizajes
│   │
│   ├── monitoring/               # Sistema de monitorización
│   │   ├── __init__.py
│   │   ├── status.py            # Estado del sistema
│   │   ├── metrics.py           # Métricas del sistema
│   │   └── alerts.py            # Sistema de alertas
│   │
│   ├── logs/                     # Sistema de logging
│   │   ├── __init__.py
│   │   ├── .gitkeep
│   │   └── logger.py            # Configuración de logging
│   │
│   ├── config/                   # Configuraciones
│   │   ├── __init__.py
│   │   ├── settings.py          # Configuraciones generales
│   │   ├── log_config.py        # Configuración de logs
│   │   └── logging.py           # Configuración adicional de logs
│   │
│   └── utils/                    # Utilidades
│       ├── __init__.py
│       ├── db.py                # Utilidades de base de datos
│       └── helpers.py           # Funciones auxiliares
│
├── tests/                        # Tests unitarios y de integración
│   ├── __init__.py
│   ├── test_api/                # Tests de API
│   ├── test_core/               # Tests del sistema core
│   ├── test_knowledge/          # Tests de gestión de conocimiento
│   └── test_vectorstore/        # Tests de vectorización
│
├── docs/                         # Documentación
│   ├── api/                     # Documentación de API
│   ├── architecture/            # Documentación de arquitectura
│   └── deployment/              # Documentación de despliegue
│
└── logs/                        # Archivos de log
    ├── .gitkeep
    ├── api/                     # Logs de API
    ├── app/                     # Logs de aplicación
    ├── error/                   # Logs de errores
    └── audit/                   # Logs de auditoría
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
