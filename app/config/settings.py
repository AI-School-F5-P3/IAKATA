from pydantic_settings import BaseSettings
from pathlib import Path
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_NAME: str = "IAKATA"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Configuración de directorios
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    VECTOR_STORE_DIR: Path = BASE_DIR / "vectorstore/processed/vectors"
    CACHE_DIR: Path = BASE_DIR / "vectorstore/cache"
    LOG_DIR: Path = BASE_DIR / "../logs"
    
    # Configuración de OpenAI
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4"
    DEFAULT_TEMPERATURE: float = 0.7
    
    # Configuración de Vector Store
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    BATCH_SIZE: int = 32
    
    # Configuración MySQL (opcional por ahora)
    MYSQL_HOST: Optional[str] = None
    MYSQL_PORT: Optional[int] = None
    MYSQL_DB: Optional[str] = None
    MYSQL_USER: Optional[str] = None
    MYSQL_PASSWORD: Optional[str] = None
    MYSQL_CHARSET: str = "utf8mb4"
    MYSQL_POOL_SIZE: int = 5
    MYSQL_POOL_RECYCLE: int = 3600
    
    # URL de conexión MySQL (solo si están definidos los valores)
    @property
    def MYSQL_URL(self) -> Optional[str]:
        if all([self.MYSQL_HOST, self.MYSQL_PORT, self.MYSQL_DB, 
                self.MYSQL_USER, self.MYSQL_PASSWORD]):
            return (
                f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
                f"?charset={self.MYSQL_CHARSET}"
            )
        return None
    
    # Configuración de la API
    API_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: list = ["*"]
    
    # Timeouts y límites
    VECTOR_SEARCH_TIMEOUT: int = 30  # segundos
    LLM_TIMEOUT: int = 60  # segundos
    MAX_RETRIES: int = 3
    
    # Cache settings
    CACHE_EMBEDDINGS: bool = True
    CACHE_TTL: int = 3600  # 1 hora
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()