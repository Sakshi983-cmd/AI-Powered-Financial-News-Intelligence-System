"""
Configuration Management for Tradl Hackathon
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Centralized configuration management"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
    
    @property
    def anthropic_api_key(self) -> str:
        """Get Anthropic API key from environment"""
        return os.getenv("ANTHROPIC_API_KEY", "")
    
    @property
    def vector_db_path(self) -> Path:
        """Get vector database path"""
        return Path(self.get('paths.chroma_dir', 'chroma_db'))
    
    @property
    def data_path(self) -> Path:
        """Get data directory path"""
        return Path(self.get('paths.data_dir', 'data'))
    
    def create_directories(self):
        """Create necessary directories"""
        self.vector_db_path.mkdir(exist_ok=True)
        self.data_path.mkdir(exist_ok=True)
        Path(self.get('paths.logs_dir', 'logs')).mkdir(exist_ok=True)

# Global config instance
config = Config()
config.create_directories()