import sys
from pathlib import Path
import pytest

# Añade el directorio raíz y app al path
root = Path(__file__).parent
app_path = root / 'app'

sys.path.insert(0, str(root))
sys.path.insert(0, str(app_path))

# Configuración para pytest-asyncio
pytest.ini_options = {
    "asyncio_mode": "strict",
    "asyncio_default_fixture_loop_scope": "function"
}