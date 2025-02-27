# app/analysis/db_connector.py

import logging
import aiohttp
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class AnalysisDBConnector:
    """
    Conector para obtener datos de la base de datos de LKWEB.
    En lugar de conectarse directamente a la base de datos, usa la API de LKWEB.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:5001"):
        """
        Inicializa el conector.
        
        Args:
            api_base_url: URL base de la API de LKWEB
        """
        self.api_base_url = api_base_url
        
    async def fetch_one(self, endpoint: str, conditions: Dict) -> Optional[Dict]:
        """
        Obtiene un único registro que cumple con las condiciones.
        
        Args:
            endpoint: Endpoint de la API (ej: 'processes', 'challenges')
            conditions: Diccionario con condiciones de filtrado
            
        Returns:
            Diccionario con los datos o None si no se encuentra
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Construir parámetros de query
                params = {k: v for k, v in conditions.items() if v is not None}
                
                # Realizar petición
                url = f"{self.api_base_url}/{endpoint}"
                if 'id' in conditions:
                    url = f"{url}/{conditions['id']}"
                    
                async with session.get(url, params=params) as response:
                    if response.status == 404:
                        return None
                        
                    if response.status != 200:
                        logger.error(f"Error fetching from {endpoint}: {response.status}")
                        return None
                        
                    data = await response.json()
                    
                    # Si es una colección, retornamos el primer elemento
                    if isinstance(data, list) and data:
                        return data[0]
                    return data
                    
        except Exception as e:
            logger.error(f"Error in fetch_one({endpoint}): {str(e)}")
            return None
            
    async def fetch_all(self, endpoint: str, conditions: Optional[Dict] = None) -> List[Dict]:
        """
        Obtiene todos los registros que cumplen con las condiciones.
        
        Args:
            endpoint: Endpoint de la API
            conditions: Diccionario con condiciones de filtrado (opcional)
            
        Returns:
            Lista de diccionarios con los datos
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Construir parámetros de query
                params = {}
                if conditions:
                    params = {k: v for k, v in conditions.items() if v is not None}
                
                # Realizar petición
                url = f"{self.api_base_url}/{endpoint}"
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Error fetching from {endpoint}: {response.status}")
                        return []
                        
                    data = await response.json()
                    
                    # Manejar diferentes formatos de respuesta
                    if isinstance(data, dict):
                        if 'data' in data:
                            return data['data']
                        return [data]
                    
                    return data if isinstance(data, list) else []
                    
        except Exception as e:
            logger.error(f"Error in fetch_all({endpoint}): {str(e)}")
            return []
    
    async def fetch_analyses(self, project_id: str, from_date=None) -> List[Dict]:
        """
        Obtiene análisis históricos para un proyecto.
        
        Args:
            project_id: ID del proyecto
            from_date: Fecha desde la cual obtener análisis
            
        Returns:
            Lista de análisis históricos
        """
        # Ejemplo: en un sistema real, esto obtendría datos históricos
        # Para simplificar, generamos datos de ejemplo
        return [
            {
                "analyzed_at": "2023-09-15T10:30:00",
                "metrics": {
                    "overall_score": 0.72,
                    "process_adherence": 0.80,
                    "target_achievement": 0.65
                }
            },
            {
                "analyzed_at": "2023-09-08T14:20:00",
                "metrics": {
                    "overall_score": 0.68,
                    "process_adherence": 0.75,
                    "target_achievement": 0.60
                }
            }
        ]
        
    async def fetch_active_projects(self) -> List[Dict]:
        """
        Obtiene todos los proyectos activos.
        
        Returns:
            Lista de proyectos activos
        """
        # En este ejemplo, simplemente obtenemos todos los retos
        return await self.fetch_all("challenge")