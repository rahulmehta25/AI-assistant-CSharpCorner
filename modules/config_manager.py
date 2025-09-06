import os
import yaml
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = {}
        self.load_config()
        load_dotenv()
    
    def load_config(self):
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.create_default_config()
    
    def create_default_config(self):
        default_config = {
            'api_keys': {
                'openai': os.getenv('OPENAI_API_KEY', ''),
                'indeed': os.getenv('INDEED_API_KEY', ''),
                'linkedin': os.getenv('LINKEDIN_API_KEY', ''),
            },
            'database': {
                'type': 'sqlite',
                'path': 'data/users.db'
            },
            'scraping': {
                'cache_duration': 86400,  # 24 hours in seconds
                'max_retries': 3,
                'timeout': 30
            },
            'careers': {
                'data_path': 'data/careers/',
                'roadmap_path': 'data/roadmap_templates/'
            },
            'ui': {
                'theme': 'default',
                'max_file_size': 10485760  # 10MB
            }
        }
        
        self.config = default_config
        self.save_config()
    
    def save_config(self):
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()