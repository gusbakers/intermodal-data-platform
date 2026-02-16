"""
Configuration management
WHY: Centralized settings = easier maintenance & deployment
"""
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """
    Load and parse YAML configuration
    
    Benefits:
    - Single source of truth
    - Easy environment switching (dev/prod)
    - No hardcoded values
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get config value using dot notation
        Example: config.get('data.raw_file')
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

# Global config instance
config = ConfigLoader()
