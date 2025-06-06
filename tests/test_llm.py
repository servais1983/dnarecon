import pytest
import json
from pathlib import Path
from core.llm import LLMAnnotator, run
from unittest.mock import patch, mock_open

@pytest.fixture
def sample_behavior_data():
    return {
        "url": "http://test.com",
        "status_code": 200,
        "response_time": 0.5,
        "headers": {
            "Content-Type": "text/html",
            "X-Frame-Options": "DENY"
        },
        "body": "<html><body>Test</body></html>"
    }

@pytest.fixture
def mock_llm_response():
    return {
        "choices": [{
            "message": {
                "content": """
                Security implications:
                - X-Frame-Options header is properly set
                - No sensitive information in response
                
                Potential vulnerabilities:
                - No Content-Security-Policy header
                
                Recommended actions:
                - Add Content-Security-Policy header
                - Implement rate limiting
                """
            }
        }],
        "created": 1234567890,
        "model": "gpt-4"
    }

def test_llm_annotator_init():
    """Teste l'initialisation de l'annotateur LLM."""
    with patch('os.getenv', return_value="test_api_key"):
        annotator = LLMAnnotator()
        assert annotator.api_key == "test_api_key"

def test_llm_annotator_init_no_key():
    """Teste l'initialisation sans clé API."""
    with patch('os.getenv', return_value=None), \
         patch('pathlib.Path.exists', return_value=False), \
         pytest.raises(ValueError):
        LLMAnnotator()

def test_analyze_behavior(sample_behavior_data, mock_llm_response):
    """Teste l'analyse de comportement."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_llm_response
        mock_post.return_value.status_code = 200
        
        annotator = LLMAnnotator(api_key="test_key")
        result = annotator.analyze_behavior(sample_behavior_data)
        
        assert "original_data" in result
        assert "annotations" in result
        assert "confidence_score" in result
        assert result["original_data"] == sample_behavior_data

def test_analyze_behavior_api_error(sample_behavior_data):
    """Teste la gestion des erreurs API."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 401
        mock_post.return_value.text = "Invalid API key"
        
        annotator = LLMAnnotator(api_key="test_key")
        with pytest.raises(Exception) as exc_info:
            annotator.analyze_behavior(sample_behavior_data)
        assert "LLM API error" in str(exc_info.value)

def test_run_function(sample_behavior_data, mock_llm_response, tmp_path):
    """Teste la fonction run."""
    input_file = tmp_path / "input.json"
    with open(input_file, 'w') as f:
        json.dump(sample_behavior_data, f)

    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_llm_response
        mock_post.return_value.status_code = 200

        with patch.dict('os.environ', {'LLM_API_KEY': 'test_key'}):
            run(str(input_file))
            mock_post.assert_called_once()

def test_run_function_file_not_found():
    """Teste la fonction run avec un fichier inexistant."""
    with pytest.raises(FileNotFoundError):
        run("nonexistent.json")

def test_run_function_invalid_json(tmp_path):
    """Teste la fonction run avec un JSON invalide."""
    input_file = tmp_path / "input.json"
    with open(input_file, 'w') as f:
        f.write("invalid json")
    
    with pytest.raises(json.JSONDecodeError):
        run(str(input_file))

def test_prepare_analysis_prompt(sample_behavior_data):
    """Teste la préparation du prompt d'analyse."""
    annotator = LLMAnnotator(api_key="test_key")
    prompt = annotator._prepare_analysis_prompt(sample_behavior_data)

    assert "URL: http://test.com" in prompt
    assert "Response Status: 200" in prompt
    assert "Response Time: 0.5" in prompt
    assert "Headers: {" in prompt
    assert '"X-Frame-Options": "DENY"' in prompt
    assert "Body: <html><body>Test</body></html>" in prompt

def test_process_llm_response(mock_llm_response):
    """Teste le traitement de la réponse LLM."""
    annotator = LLMAnnotator(api_key="test_key")
    result = annotator._process_llm_response(mock_llm_response)
    
    assert "analysis" in result
    assert "timestamp" in result
    assert "model" in result
    assert result["model"] == "gpt-4"

def test_calculate_confidence():
    """Teste le calcul du score de confiance."""
    annotator = LLMAnnotator(api_key="test_key")
    confidence = annotator._calculate_confidence({
        "analysis": "Test analysis",
        "timestamp": 1234567890,
        "model": "gpt-4"
    })
    
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 1 