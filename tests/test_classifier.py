import pytest
import json
from pathlib import Path
from core.classifier import run
from unittest.mock import patch, mock_open
from unittest.mock import call

@pytest.fixture
def sample_results():
    return [
        {
            "url": "http://test.com/xss",
            "status": 200,
            "body": "<script>alert(1)</script>",
            "attack": "xss"
        },
        {
            "url": "http://test.com/sqli",
            "status": 403,
            "body": "Access Denied",
            "attack": "sqli"
        },
        {
            "url": "http://test.com/normal",
            "status": 200,
            "body": "Welcome",
            "attack": "normal"
        }
    ]

def test_classifier_vulnerable(sample_results, tmp_path):
    """Teste la classification d'une réponse vulnérable."""
    results_file = tmp_path / "results.json"
    with open(results_file, 'w') as f:
        json.dump(sample_results, f)
    
    with patch('builtins.print') as mock_print:
        run(str(results_file))
        mock_print.assert_any_call("[!] Comportement VULNÉRABLE pour attaque xss → http://test.com/xss")

def test_classifier_strict(sample_results, tmp_path):
    """Teste la classification d'une réponse stricte."""
    results_file = tmp_path / "results.json"
    with open(results_file, 'w') as f:
        json.dump(sample_results, f)
    
    with patch('builtins.print') as mock_print:
        run(str(results_file))
        mock_print.assert_any_call("[+] Comportement STRICT pour attaque sqli → http://test.com/sqli")

def test_classifier_flexible(sample_results, tmp_path):
    """Teste la classification d'une réponse flexible."""
    results_file = tmp_path / "results.json"
    with open(results_file, 'w') as f:
        json.dump(sample_results, f)
    
    with patch('builtins.print') as mock_print:
        run(str(results_file))
        mock_print.assert_any_call("[~] Comportement FLEXIBLE pour attaque normal → http://test.com/normal")

def test_classifier_file_not_found():
    """Teste le comportement avec un fichier inexistant."""
    with pytest.raises(FileNotFoundError):
        run("nonexistent.json")

def test_classifier_invalid_json(tmp_path):
    """Teste le comportement avec un JSON invalide."""
    results_file = tmp_path / "results.json"
    with open(results_file, 'w') as f:
        f.write("invalid json")
    
    with pytest.raises(json.JSONDecodeError):
        run(str(results_file))

def test_classifier_empty_file(tmp_path):
    """Teste le comportement avec un fichier vide."""
    results_file = tmp_path / "results.json"
    with open(results_file, 'w') as f:
        json.dump([], f)

    with patch('builtins.print') as mock_print:
        run(str(results_file))
        mock_print.assert_called_once_with(f"[*] Classification des réponses depuis {results_file}")

def test_classifier_missing_fields(tmp_path):
    """Teste le comportement avec des champs manquants."""
    results_file = tmp_path / "results.json"
    with open(results_file, 'w') as f:
        json.dump([{
            "url": "http://test.com",
            "status_code": 200,
            "headers": {"Content-Type": "text/html"},
            "body": "<html><body>Test</body></html>",
            "status": "success",
            "attack": "normal"
        }], f)

    with patch('builtins.print') as mock_print:
        run(str(results_file))
        mock_print.assert_has_calls([
            call(f"[*] Classification des réponses depuis {results_file}"),
            call('[~] Comportement FLEXIBLE pour attaque normal → http://test.com')
        ])

def test_classifier_syntax_error(tmp_path):
    """Teste la détection d'erreurs de syntaxe."""
    results_file = tmp_path / "results.json"
    with open(results_file, 'w') as f:
        json.dump([{
            "url": "http://test.com/syntax",
            "status": 200,
            "body": "syntax error in response",
            "attack": "syntax"
        }], f)
    
    with patch('builtins.print') as mock_print:
        run(str(results_file))
        mock_print.assert_any_call("[!] Comportement VULNÉRABLE pour attaque syntax → http://test.com/syntax") 