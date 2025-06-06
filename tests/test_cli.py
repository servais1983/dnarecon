import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import os
from pathlib import Path
from dnarecon import main
import asyncio
from unittest.mock import mock_open
import argparse

@pytest.fixture
def mock_analyzer():
    with patch('core.analyzer.run') as mock:
        mock.return_value = {
            "status_code": 200,
            "headers": {"Content-Type": "text/html"},
            "body": "<html><body>Test</body></html>"
        }
        yield mock

@pytest.fixture
def mock_classifier():
    with patch('core.classifier.run') as mock:
        mock.return_value = None
        yield mock

@pytest.fixture
def mock_llm():
    with patch('core.llm.run') as mock:
        mock.return_value = None
        yield mock

@pytest.fixture
def mock_utils():
    with patch('core.utils.run_script_yaml') as mock:
        mock.return_value = None
        yield mock

@pytest.mark.asyncio
async def test_analyze_command():
    """Test de la commande analyze."""
    with patch('core.analyzer.run', new_callable=AsyncMock) as mock:
        with patch('sys.argv', ['dnarecon', 'analyze', 'http://test.com']):
            await main()
            mock.assert_called_once_with('http://test.com', is_async=True)

def test_classify_command():
    """Test de la commande classify."""
    with patch('core.classifier.run') as mock:
        with patch('sys.argv', ['dnarecon', 'classify', 'results.json']):
            asyncio.run(main())
            mock.assert_called_once_with('results.json')

def test_llm_tag_command():
    """Test de la commande llm-tag."""
    with patch('core.llm.run') as mock:
        with patch('sys.argv', ['dnarecon', 'llm-tag', 'results.json']):
            asyncio.run(main())
            mock.assert_called_once_with('results.json')

@pytest.mark.asyncio
async def test_run_command():
    """Test de la commande run."""
    mock_run = AsyncMock()
    mock_run.return_value = None

    with patch('dnarecon.__main__.run_script_yaml', mock_run):
        with patch('sys.argv', ['dnarecon', 'run', 'script.yaml']):
            with patch('builtins.open', mock_open(read_data=b'url: http://test.com')):
                with patch('os.path.exists', return_value=True):
                    with patch('argparse.ArgumentParser._get_formatter'):
                        with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                            mock_parse.return_value = argparse.Namespace(
                                command='run',
                                file='script.yaml'
                            )
                            await main()
                            mock_run.assert_called_once_with('script.yaml')

def test_invalid_command():
    """Test d'une commande invalide."""
    with patch('sys.argv', ['dnarecon', 'invalid']):
        with pytest.raises(SystemExit):
            asyncio.run(main())

def test_missing_argument():
    """Test avec un argument manquant."""
    with patch('sys.argv', ['dnarecon', 'analyze']):
        with pytest.raises(SystemExit):
            asyncio.run(main()) 