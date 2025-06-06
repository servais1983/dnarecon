import os
from pathlib import Path
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".dnarecon"
        self.config_file = self.config_dir / "config.json"
        self.default_config = {
            "llm_api_key": "",
            "timeout": 30,
            "max_retries": 3,
            "user_agent": "DNARecon/1.0",
            "proxy": None,
            "log_level": "INFO",
            "output_dir": str(self.config_dir / "outputs"),
            "temp_dir": str(self.config_dir / "temp"),
            "allowed_domains": [],
            "excluded_paths": ["/logout", "/admin"],
            "rate_limit": {
                "requests_per_second": 2,
                "burst": 5
            },
            "security": {
                "verify_ssl": True,
                "follow_redirects": True,
                "max_redirects": 5
            },
            "target": "",
            "async": False
        }
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier ou crée une nouvelle si nécessaire."""
        try:
            if not self.config_dir.exists():
                self.config_dir.mkdir(parents=True)
            
            if not self.config_file.exists():
                self._save_config(self.default_config)
                return self.default_config
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Fusionne avec la configuration par défaut
                return {**self.default_config, **config}
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
            return self.default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Sauvegarde la configuration dans le fichier."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Définit une valeur de configuration."""
        self.config[key] = value
        self._save_config(self.config)

    def update(self, config_dict: Dict[str, Any]) -> None:
        """Met à jour plusieurs valeurs de configuration."""
        self.config.update(config_dict)
        self._save_config(self.config)

    def reset(self) -> None:
        """Réinitialise la configuration aux valeurs par défaut."""
        self.config = self.default_config.copy()
        self._save_config(self.config)

    def __getitem__(self, key: str) -> Any:
        """Permet l'accès aux valeurs de configuration via config['key']."""
        return self.config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Permet la modification des valeurs via config['key'] = value."""
        self.set(key, value)

# Instance globale de configuration
config = Config() 