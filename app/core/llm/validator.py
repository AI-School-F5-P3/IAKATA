import json
from typing import Dict, List

class ResponseValidator:
    @staticmethod
    def process_validation(content: str) -> Dict[str, bool]:
        """Process validation response to extract validation results"""
        try:
            if '{' in content and '}' in content:
                validation_part = content[content.find('{'):content.rfind('}')+1]
                return json.loads(validation_part)
            return {"valid": True if "válido" in content.lower() else False}
        except:
            return {"error": "Could not parse validation results"}

    @staticmethod
    def process_suggestions(content: str) -> List[str]:
        """Process suggestion response to extract list of suggestions"""
        suggestions = [s.strip() for s in content.split('\n') 
                      if s.strip().startswith(('-', '•', '*', '1.'))]
        return suggestions if suggestions else [content]