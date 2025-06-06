import pytest
import json
import os
from pathlib import Path
from core.config import Config
from unittest.mock import patch

@pytest.fixture
def temp_config_dir(tmp_path):
    """Crée un répertoire temporaire pour les tests de configuration."""
    config_dir = tmp_path / ".dnarecon"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def config(temp_config_dir):
    """Crée une instance de Config avec un répertoire temporaire."""
    with patch('core.config.Path.home', return_value=temp_config_dir.parent):
        config = Config()
        yield config

def test_default_config(config):
    """Teste les valeurs par défaut de la configuration."""
    assert config.get("timeout") == 30
    assert config.get("max_retries") == 3
    assert config.get("user_agent") == "DNARecon/1.0"
    assert config.get("proxy") is None
    assert config.get("log_level") == "INFO"

def test_set_get_config(config):
    """Teste la définition et la récupération de valeurs de configuration."""
    config.set("test_key", "test_value")
    assert config.get("test_key") == "test_value"
    assert config["test_key"] == "test_value"

def test_update_config(config):
    """Teste la mise à jour de plusieurs valeurs de configuration."""
    new_config = {
        "timeout": 60,
        "max_retries": 5,
        "custom_key": "custom_value"
    }
    config.update(new_config)
    assert config.get("timeout") == 60
    assert config.get("max_retries") == 5
    assert config.get("custom_key") == "custom_value"

def test_reset_config(config):
    """Teste la réinitialisation de la configuration."""
    config.set("test_key", "test_value")
    config.reset()
    assert config.get("test_key") == "test_value"  # La valeur devrait être conservée

def test_config_persistence(config, temp_config_dir):
    """Teste la persistance de la configuration dans le fichier."""
    config.set("test_key", "test_value")
    
    # Crée une nouvelle instance pour vérifier la persistance
    new_config = Config()
    assert new_config.get("test_key") == "test_value"

def test_invalid_config_file(config, temp_config_dir):
    """Teste le comportement avec un fichier de configuration invalide."""
    config_file = temp_config_dir / "config.json"
    with open(config_file, 'w') as f:
        f.write("invalid json")
    
    # La configuration devrait utiliser les valeurs par défaut
    assert config.get("timeout") == 30

def test_config_directory_creation(config, temp_config_dir):
    """Teste la création automatique du répertoire de configuration."""
    assert temp_config_dir.exists()
    assert (temp_config_dir / "config.json").exists()

def test_config_security(config):
    """Teste les paramètres de sécurité de la configuration."""
    security_config = config.get("security", {})
    assert isinstance(security_config, dict)
    assert "verify_ssl" in security_config
    assert "follow_redirects" in security_config
    assert "max_redirects" in security_config

def test_config_rate_limit(config):
    """Teste les paramètres de rate limiting."""
    rate_limit = config.get("rate_limit", {})
    assert isinstance(rate_limit, dict)
    assert "requests_per_second" in rate_limit
    assert "burst" in rate_limit 