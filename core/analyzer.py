import aiohttp
import asyncio
import logging
from typing import Dict, Optional, Union, Awaitable, Any, List
import requests
import json
from urllib.parse import urlparse
from time import time
from .config import config

logger = logging.getLogger(__name__)

class DNAReconError(Exception):
    """Classe de base pour les exceptions DNARecon."""
    pass

class ValidationError(DNAReconError):
    """Erreur de validation des entrées."""
    pass

class RequestError(DNAReconError):
    """Erreur lors d'une requête HTTP."""
    pass

class TimeoutError(DNAReconError):
    """Erreur de timeout."""
    pass

class SecurityError(DNAReconError):
    """Erreur liée à la sécurité."""
    pass

# Configuration de sécurité
DEFAULT_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'self'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
}

# Configuration des retries
RETRY_COUNT = 3
RETRY_DELAY = 1.0  # secondes

# Liste de User-Agents pour la rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
]

TIMEOUT_CONFIG = {
    "total": 30.0,  # Timeout total pour toute l'opération
    "connect": 5.0,  # Timeout pour la connexion
    "sock_read": 10.0,  # Timeout pour la lecture
    "sock_connect": 5.0  # Timeout pour la connexion socket
}

MUTATIONS = [
    ("xss", "<script>alert(1)</script>"),
    ("sqli", "' OR '1'='1"),
    ("idor", "user_id=1", "user_id=2"),
]

class RateLimiter:
    def __init__(self, max_requests: int, time_window: float):
        self.semaphore = asyncio.Semaphore(max_requests)
        self.time_window = time_window
        self.last_reset = time()
        self.requests = 0
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            current_time = time()
            if current_time - self.last_reset >= self.time_window:
                self.requests = 0
                self.last_reset = current_time
            
            if self.requests >= self.semaphore._value:
                wait_time = self.time_window - (current_time - self.last_reset)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                self.requests = 0
                self.last_reset = time()
            
            await self.semaphore.acquire()
            self.requests += 1

    def release(self):
        self.semaphore.release()

class ResponseCache:
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                if time() - entry['timestamp'] < self.ttl:
                    return entry['data']
                else:
                    del self.cache[key]
        return None

    async def set(self, key: str, data: Dict[str, Any]) -> None:
        async with self._lock:
            if len(self.cache) >= self.max_size:
                # Supprime l'entrée la plus ancienne
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
                del self.cache[oldest_key]
            
            self.cache[key] = {
                'data': data,
                'timestamp': time()
            }

    async def clear(self) -> None:
        """Vide le cache."""
        async with self._lock:
            self.cache.clear()

    async def size(self) -> int:
        """Retourne le nombre d'entrées dans le cache."""
        async with self._lock:
            return len(self.cache)

    async def get_expired_entries(self) -> List[str]:
        """Retourne la liste des clés expirées."""
        async with self._lock:
            current_time = time()
            return [
                key for key, entry in self.cache.items()
                if current_time - entry['timestamp'] >= self.ttl
            ]

# Instance globale du cache
response_cache = ResponseCache()

def validate_url(url: str) -> Optional[str]:
    """Valide et nettoie l'URL."""
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValidationError(f"URL invalide: schéma ou domaine manquant")
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError(f"Schéma non supporté: {parsed.scheme}")
        if len(parsed.netloc) > 255:
            raise ValidationError("Domaine trop long")
        if any(char in parsed.netloc for char in ['<', '>', '"', "'", '%']):
            raise ValidationError("Caractères non autorisés dans le domaine")
        return url
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Erreur de validation de l'URL: {str(e)}")

def get_random_user_agent() -> str:
    """Retourne un User-Agent aléatoire."""
    import random
    return random.choice(USER_AGENTS)

async def _async_request(url: str, custom_headers: Optional[Dict] = None, use_cache: bool = True) -> Dict[str, Any]:
    """Effectue une requête HTTP asynchrone avec support du cache et des retries."""
    if not validate_url(url):
        raise ValidationError(f"URL invalide: {url}")

    # Vérifie le cache si activé
    if use_cache:
        cached_response = await response_cache.get(url)
        if cached_response:
            logger.debug(f"Utilisation de la réponse en cache pour {url}")
            return cached_response

    headers = {
        **DEFAULT_SECURITY_HEADERS,
        "User-Agent": get_random_user_agent(),
        **(custom_headers or {})
    }

    last_error = None
    for attempt in range(RETRY_COUNT):
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(**TIMEOUT_CONFIG),
                    ssl=config.get("security", {}).get("verify_ssl", True)
                )
                
                if response.status >= 400:
                    text = await response.text()
                    raise RequestError(f"Erreur HTTP {response.status}: {text}")

                result = {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "body": await response.text()
                }

                # Met en cache la réponse si le cache est activé
                if use_cache and response.status == 200:
                    await response_cache.set(url, result)

                return result

        except (asyncio.TimeoutError, aiohttp.ClientError, RequestError) as e:
            last_error = e
            if attempt < RETRY_COUNT - 1:
                logger.warning(f"Tentative {attempt + 1}/{RETRY_COUNT} échouée pour {url}: {str(e)}")
                await asyncio.sleep(RETRY_DELAY)
            continue
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la requête vers {url}: {str(e)}")
            raise DNAReconError(f"Erreur inattendue: {str(e)}")

    # Si toutes les tentatives ont échoué
    if last_error is None:
        raise DNAReconError(f"Erreur inconnue lors de la requête vers {url}")
    elif isinstance(last_error, asyncio.TimeoutError):
        raise TimeoutError(f"Timeout lors de la requête vers {url}")
    elif isinstance(last_error, aiohttp.ClientError):
        raise RequestError(f"Erreur client: {str(last_error)}")
    elif isinstance(last_error, RequestError):
        raise last_error
    else:
        raise DNAReconError(f"Erreur inattendue: {str(last_error)}")

def _sync_request(url: str, custom_headers: Optional[Dict] = None) -> Dict[str, Any]:
    """Effectue une requête HTTP synchrone."""
    if not validate_url(url):
        raise ValidationError(f"URL invalide: {url}")

    headers = {
        **DEFAULT_SECURITY_HEADERS,
        "User-Agent": get_random_user_agent(),
        **(custom_headers or {})
    }
    
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=config.get("timeout", 30),
            verify=config.get("security", {}).get("verify_ssl", True)
        )
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text
        }
    except requests.Timeout:
        logger.error(f"Timeout lors de la requête vers {url}")
        raise TimeoutError(f"Timeout lors de la requête vers {url}")
    except requests.RequestException as e:
        logger.error(f"Erreur lors de la requête vers {url}: {str(e)}")
        raise RequestError(f"Erreur client: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la requête vers {url}: {str(e)}")
        raise DNAReconError(f"Erreur inattendue: {str(e)}")

async def run(url: str, custom_headers: Optional[Dict] = None, is_async: bool = True, use_cache: bool = True) -> Dict[str, Any]:
    """
    Analyse une URL et retourne les résultats.
    
    Args:
        url: L'URL à analyser
        custom_headers: Headers HTTP personnalisés
        is_async: Si True, utilise une requête asynchrone
        use_cache: Si True, utilise le cache pour les réponses
    
    Returns:
        Dict contenant les résultats de l'analyse
    """
    try:
        if is_async:
            return await _async_request(url, custom_headers, use_cache)
        return await asyncio.to_thread(_sync_request, url, custom_headers)
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de {url}: {str(e)}")
        raise

def print_results(results: Dict[str, Any]) -> None:
    """Affiche les résultats de l'analyse de manière sécurisée."""
    print("[*] Analyse de comportement vers :", results.get("url", "N/A"))
    print("Status:", results.get("status_code", "N/A"))
    print("Headers:", {k: v for k, v in results.get("headers", {}).items() if not k.lower().startswith(("cookie", "authorization"))})
    print("Body:", results.get("body", "")[:300])

async def process_attacks_async(target: str, rate_limiter: RateLimiter) -> List[Dict[str, Any]]:
    """Traite les attaques de manière asynchrone avec rate limiting."""
    results = []
    for attack in MUTATIONS:
        if attack[0] == "idor":
            payloads = [attack[1], attack[2]]
        else:
            payloads = [f"?input={attack[1]}"]

        for p in payloads:
            try:
                await rate_limiter.acquire()
                full_url = target + p
                res = await _async_request(full_url)
                results.append({
                    "url": full_url,
                    "status": res["status_code"],
                    "headers": res["headers"],
                    "body": res["body"],
                    "attack": attack[0]
                })
            except Exception as e:
                results.append({
                    "url": target + p,
                    "status": "ERROR",
                    "body": str(e),
                    "attack": attack[0]
                })
            finally:
                rate_limiter.release()
    return results

def process_attacks_sync(target: str) -> List[Dict[str, Any]]:
    """Traite les attaques de manière synchrone."""
    results = []
    for attack in MUTATIONS:
        if attack[0] == "idor":
            payloads = [attack[1], attack[2]]
        else:
            payloads = [f"?input={attack[1]}"]

        for p in payloads:
            try:
                full_url = target + p
                res = _sync_request(full_url)
                results.append({
                    "url": full_url,
                    "status": res["status_code"],
                    "headers": res["headers"],
                    "body": res["body"],
                    "attack": attack[0]
                })
            except Exception as e:
                results.append({
                    "url": target + p,
                    "status": "ERROR",
                    "body": str(e),
                    "attack": attack[0]
                })
    return results

def main():
    """Point d'entrée principal avec gestion des erreurs et logging."""
    try:
        target = config['target']
        if not validate_url(target):
            raise ValueError(f"URL cible invalide: {target}")

        print(f"Analyse de comportement vers : {target}")
        
        if config['async']:
            rate_limiter = RateLimiter(
                max_requests=config.get("rate_limit", {}).get("requests_per_second", 2),
                time_window=1.0
            )
            results = asyncio.run(process_attacks_async(target, rate_limiter))
        else:
            results = process_attacks_sync(target)

        with open("dna_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("[+] Résultats enregistrés dans dna_results.json")

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution: {str(e)}")
        raise

if __name__ == "__main__":
    main()