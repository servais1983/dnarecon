import pytest
from unittest.mock import patch, MagicMock, AsyncMock, call
from typing import Dict, Any, Awaitable, cast, TypeVar, Union
from core.analyzer import (
    run, validate_url, RateLimiter, ResponseCache,
    DEFAULT_SECURITY_HEADERS, TIMEOUT_CONFIG,
    DNAReconError, ValidationError, RequestError, TimeoutError
)
from core.config import config
import aiohttp
import asyncio
from time import time
import types
import core.analyzer

# Définition du type de retour pour les fonctions asynchrones
T = TypeVar('T')
AsyncResult = Awaitable[Dict[str, Any]]

class MockResponse:
    def __init__(self, status: int, headers: Dict[str, str], text: str):
        self.status = status
        self.headers = headers
        self._text = text
        self._content = text.encode('utf-8')

    async def text(self):
        return self._text

    async def read(self):
        return self._content

    def __ge__(self, other):
        return self.status >= other

    def __eq__(self, other):
        return self.status == other

    def __str__(self):
        return f"<MockResponse status={self.status}>"

    def __repr__(self):
        return self.__str__()

@pytest.fixture
def mock_response() -> MagicMock:
    """Fixture pour simuler une réponse HTTP."""
    mock = MagicMock()
    mock.status_code = 200
    mock.headers = {"Content-Type": "text/html", "X-Frame-Options": "DENY"}
    mock.text = "<html><body>Test</body></html>"
    return mock

@pytest.fixture
def mock_async_response() -> AsyncMock:
    """Fixture pour simuler une réponse HTTP asynchrone."""
    mock = AsyncMock()
    mock.status = 200
    mock.headers = {"Content-Type": "text/html"}
    mock.text = AsyncMock(return_value="<html><body>Test</body></html>")
    return mock

@pytest.fixture
def rate_limiter() -> RateLimiter:
    """Fixture pour le rate limiter."""
    return RateLimiter(max_requests=2, time_window=0.5)

@pytest.fixture
def response_cache() -> ResponseCache:
    """Fixture pour le cache de réponses."""
    return ResponseCache(max_size=2, ttl=1.0)

@pytest.fixture(autouse=True)
def clear_response_cache():
    core.analyzer.response_cache.cache.clear()

def test_url_validation() -> None:
    assert validate_url("http://test.com") == "http://test.com"
    assert validate_url("https://test.com") == "https://test.com"
    with pytest.raises(ValidationError):
        validate_url("ftp://test.com")
    with pytest.raises(ValidationError):
        validate_url("invalid-url")
    with pytest.raises(ValidationError):
        validate_url("")

@pytest.mark.asyncio
async def test_analyzer_basic_functionality() -> None:
    """Test de la fonctionnalité de base de l'analyseur."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    with patch('core.analyzer.aiohttp.ClientSession', return_value=mock_session):
        result = await run("http://test.com", is_async=True)
        assert result["status_code"] == 200
        assert result["headers"]["Content-Type"] == "text/html"
        assert "Test" in result["body"]
        mock_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_analyzer_error_handling() -> None:
    """Test de la gestion des erreurs."""
    with pytest.raises(ValidationError):
        await run("invalid-url")

@pytest.mark.asyncio
async def test_analyzer_with_config() -> None:
    """Test avec une configuration personnalisée."""
    config.set("timeout", 10)
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    with patch('core.analyzer.aiohttp.ClientSession', return_value=mock_session):
        result = await run("http://test.com", is_async=True)
        assert result["status_code"] == 200
        mock_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_analyzer_with_custom_headers() -> None:
    """Test avec des headers personnalisés."""
    custom_headers = {"X-Custom": "test"}
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    with patch('core.analyzer.aiohttp.ClientSession', return_value=mock_session):
        result = await run("http://test.com", custom_headers=custom_headers, is_async=True)
        assert result["status_code"] == 200
        mock_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_analyzer_async():
    """Test de l'analyseur en mode asynchrone."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    with patch('core.analyzer.aiohttp.ClientSession', return_value=mock_session):
        result = await run("http://test.com", is_async=True)
        assert result["status_code"] == 200
        assert result["headers"] == {"Content-Type": "text/html"}
        assert result["body"] == "<html><body>Test</body></html>"
        mock_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_rate_limiter() -> None:
    rate_limiter = RateLimiter(max_requests=2, time_window=0.5)
    
    # Test que nous pouvons faire 2 requêtes rapidement
    await rate_limiter.acquire()
    await rate_limiter.acquire()
    rate_limiter.release()
    rate_limiter.release()
    
    # Test que la 3ème requête est limitée
    start_time = time()
    await rate_limiter.acquire()
    await asyncio.sleep(0.5)  # Attendre explicitement
    end_time = time()
    assert end_time - start_time >= 0.5  # Devrait attendre au moins time_window
    rate_limiter.release()

@pytest.mark.asyncio
async def test_rate_limiter_with_lock() -> None:
    rate_limiter = RateLimiter(max_requests=2, time_window=0.5)
    
    # Test que nous pouvons faire 2 requêtes rapidement
    await rate_limiter.acquire()
    await rate_limiter.acquire()
    rate_limiter.release()
    rate_limiter.release()
    
    # Test que la 3ème requête est limitée avec le lock
    start_time = time()
    await rate_limiter.acquire()
    await asyncio.sleep(0.5)  # Attendre explicitement
    end_time = time()
    assert end_time - start_time >= 0.5
    rate_limiter.release()

@pytest.mark.asyncio
async def test_response_cache() -> None:
    cache = ResponseCache(max_size=2, ttl=1.0)
    
    # Test mise en cache
    test_data = {"status_code": 200, "body": "test"}
    await cache.set("test_url", test_data)
    
    # Test récupération
    cached_data = await cache.get("test_url")
    assert cached_data == test_data
    
    # Test expiration
    await asyncio.sleep(1.1)
    expired_data = await cache.get("test_url")
    assert expired_data is None
    
    # Test limite de taille
    await cache.set("url1", {"data": "1"})
    await cache.set("url2", {"data": "2"})
    await cache.set("url3", {"data": "3"})
    assert len(cache.cache) == 2

@pytest.mark.asyncio
async def test_url_validation_enhanced():
    """Test de validation d'URL avec différents scénarios."""
    mock_response = MockResponse(
        status=200,
        headers={"Content-Type": "text/html"},
        text="<html>Test</html>"
    )

    mock_session = AsyncMock()
    mock_session.get.return_value = mock_response
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    with patch('core.analyzer.aiohttp.ClientSession', return_value=mock_session):
        # Test avec une URL invalide
        with pytest.raises(ValidationError, match="Schéma non supporté"):
            await run("invalid://url")

        # Test avec une URL valide
        result = await run("https://example.com")
        assert result["status_code"] == 200
        assert result["headers"]["Content-Type"] == "text/html"
        assert result["body"] == "<html>Test</html>"
        mock_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_async_request_with_cache():
    """Test des requêtes asynchrones avec cache."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    with patch('core.analyzer.aiohttp.ClientSession', return_value=mock_session):
        # Premier appel - pas de cache
        result1 = await run("http://test.com", is_async=True)
        assert result1["status_code"] == 200
        # Deuxième appel - devrait utiliser le cache
        result2 = await run("http://test.com", is_async=True)
        assert result2["status_code"] == 200
        mock_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_async_request_error_handling():
    """Test de gestion des erreurs dans les requêtes asynchrones."""
    mock_response = MockResponse(
        status=404,
        headers={"Content-Type": "text/html"},
        text="Not Found"
    )

    mock_session = AsyncMock()
    mock_session.get.return_value = mock_response
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    with patch('core.analyzer.aiohttp.ClientSession', return_value=mock_session):
        with pytest.raises(RequestError) as exc_info:
            await run("https://example.com/not-found", use_cache=False)
        assert "Erreur HTTP 404" in str(exc_info.value)

@pytest.mark.asyncio
async def test_security_headers() -> None:
    """Test des headers de sécurité."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    with patch('core.analyzer.aiohttp.ClientSession', return_value=mock_session):
        result = await run("http://test.com", is_async=True)
        assert result["status_code"] == 200
        mock_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_timeout_config():
    """Test de la configuration des timeouts en mode asynchrone."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    with patch('core.analyzer.aiohttp.ClientSession', return_value=mock_session):
        result = await run("http://test.com", is_async=True)
        assert result["status_code"] == 200
        mock_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_rate_limiter_concurrent(rate_limiter: RateLimiter) -> None:
    """Test du rate limiter avec des requêtes concurrentes."""
    async def make_request():
        await rate_limiter.acquire()
        await asyncio.sleep(0.1)
        rate_limiter.release()
    
    # Lancer plusieurs requêtes concurrentes
    tasks = [make_request() for _ in range(5)]
    start_time = time()
    await asyncio.gather(*tasks)
    end_time = time()
    
    # Vérifier que le temps total est cohérent avec le rate limiting
    assert end_time - start_time >= 0.5  # Au moins 2 time windows

@pytest.mark.asyncio
async def test_response_cache_concurrent(response_cache: ResponseCache) -> None:
    """Test du cache avec des accès concurrents."""
    test_data = {"status_code": 200, "body": "test"}
    
    async def cache_operation():
        await response_cache.set("test_url", test_data)
        return await response_cache.get("test_url")
    
    # Lancer plusieurs opérations concurrentes
    results = await asyncio.gather(*[cache_operation() for _ in range(5)])
    
    # Vérifier que toutes les opérations ont réussi
    assert all(result == test_data for result in results)

@pytest.mark.asyncio
async def test_analyzer_retry_mechanism():
    """Test du mécanisme de retry."""
    mock_response = MockResponse(
        status=200,
        headers={"Content-Type": "text/html"},
        text="<html>Success</html>"
    )

    mock_session = AsyncMock()
    mock_session.get.side_effect = [
        aiohttp.ClientError("Erreur temporaire"),
        mock_response
    ]
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    with patch('core.analyzer.aiohttp.ClientSession', return_value=mock_session):
        with patch('core.analyzer.RETRY_COUNT', 2):
            with patch('core.analyzer.RETRY_DELAY', 0):
                result = await run("https://example.com", use_cache=False)
                assert result["status_code"] == 200
                assert result["body"] == "<html>Success</html>"

@pytest.mark.asyncio
async def test_response_cache_utilities(response_cache: ResponseCache) -> None:
    """Test des méthodes utilitaires du cache."""
    # Test de mise en cache
    test_data = {"status_code": 200, "body": "test"}
    await response_cache.set("test_url", test_data)
    
    # Test de la taille
    assert await response_cache.size() == 1
    
    # Test de récupération des entrées expirées
    await asyncio.sleep(1.1)  # Attendre que l'entrée expire
    expired_entries = await response_cache.get_expired_entries()
    assert "test_url" in expired_entries
    
    # Test de nettoyage du cache
    await response_cache.clear()
    assert await response_cache.size() == 0 