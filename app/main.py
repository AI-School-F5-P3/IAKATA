from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.setup import AIComponents
from api.routes import api_router
from config.settings import get_settings
from config.logging import setup_logging
from core.auth import HeaderValidator

# Inicializar componentes
settings = get_settings()
setup_logging()

app = FastAPI(title="IAKATA")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Obtener y limpiar el prefijo API
api_prefix = settings.API_PREFIX.rstrip('/')

# Incluir router principal
app.include_router(api_router, prefix=api_prefix)

@app.on_event("startup")
async def startup_event():
    print("\nAvailable routes:")
    for route in app.routes:
        print(f"Path: {route.path}, Methods: {route.methods}")