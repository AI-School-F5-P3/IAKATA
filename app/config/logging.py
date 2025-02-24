# app/config/logging.py
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from .settings import get_settings

settings = get_settings()

def setup_logging():
    # Crear directorio de logs si no existe
    log_dir = settings.LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Formateo de logs
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo de errores
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    
    # Handler para archivo de aplicación
    app_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(log_format)
    
    # Handler para stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(log_format)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(stdout_handler)
    
    # Loggers específicos
    loggers = {
        'app.orchestrator': logging.INFO,
        'app.llm': logging.INFO,
        'app.vectorstore': logging.INFO,
        'app.retriever': logging.INFO,
        'app.api': logging.INFO
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
        # Archivo específico para cada componente
        component_handler = RotatingFileHandler(
            log_dir / f"{logger_name.split('.')[-1]}.log",
            maxBytes=10485760,
            backupCount=3,
            encoding='utf-8'
        )
        component_handler.setLevel(level)
        component_handler.setFormatter(log_format)
        logger.addHandler(component_handler)
    
    # Log de inicio de aplicación
    logging.info(f"Iniciando aplicación {settings.APP_NAME} v{settings.API_VERSION}")
    logging.info(f"Modo debug: {settings.DEBUG}")
    
class CustomLogger:
    """Logger personalizado con métodos adicionales"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def process_start(self, process_name: str, **kwargs):
        """Log de inicio de proceso con metadata"""
        self.logger.info(
            f"Iniciando {process_name} - "
            f"args: {', '.join(f'{k}={v}' for k,v in kwargs.items())}"
        )
        
    def process_end(self, process_name: str, duration: float = None):
        """Log de fin de proceso con duración opcional"""
        message = f"Finalizado {process_name}"
        if duration:
            message += f" - Duración: {duration:.2f}s"
        self.logger.info(message)
        
    def vector_search(self, query: str, results: int):
        """Log específico para búsquedas vectoriales"""
        self.logger.info(
            f"Búsqueda vectorial - Query: {query[:100]}... - "
            f"Resultados: {results}"
        )
        
    def llm_request(self, request_type: str, tokens: int):
        """Log específico para peticiones LLM"""
        self.logger.info(
            f"Petición LLM - Tipo: {request_type} - "
            f"Tokens: {tokens}"
        )
        
    def error_with_context(self, error: Exception, context: dict):
        """Log de error con contexto adicional"""
        self.logger.error(
            f"Error: {str(error)} - Contexto: {context}",
            exc_info=True
        )
        
    def warning(self, message):
        # Implementation of the warning method
        print(f"WARNING: {message}")