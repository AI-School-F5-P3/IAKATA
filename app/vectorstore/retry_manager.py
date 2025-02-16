from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Optional, List, Callable
import logging
import functools

logger = logging.getLogger(__name__)

class RetryManager:
    """
    Gestiona los reintentos de operaciones fallidas
    """
    @staticmethod
    def with_retry(
        max_attempts: int = 3,
        min_wait: int = 4,
        max_wait: int = 10
    ) -> Callable:
        """
        Decorador para añadir lógica de retry a una función
        Args:
            max_attempts: Número máximo de intentos
            min_wait: Tiempo mínimo de espera entre intentos
            max_wait: Tiempo máximo de espera entre intentos
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            @retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
                retry_error_callback=lambda retry_state: None
            )
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error en intento {retry_state.attempt_number}: {e}")
                    raise
            return wrapper
        return decorator