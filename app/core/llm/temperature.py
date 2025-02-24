from typing import Optional
from .types import ResponseType

class TemperatureManager:
    def __init__(self):
        self.temperature_settings = {
            ResponseType.CHAT: 0.7,
            ResponseType.VALIDATION: 0.1,
            ResponseType.SUGGESTION: 0.6,
            ResponseType.DOCUMENTATION: 0.4
        }
    
    def get_temperature(self, response_type: ResponseType, custom_temp: Optional[float] = None) -> float:
        """
        Get appropriate temperature for the response type
        """
        if custom_temp is not None:
            return custom_temp
        return self.temperature_settings[response_type]