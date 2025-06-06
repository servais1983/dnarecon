#!/usr/bin/env python3
"""
Exemple avancé d'utilisation de DNARecon.
Utilise des configurations personnalisées et des en-têtes HTTP.
"""

import asyncio
import json
from pathlib import Path
from core.analyzer import run, print_results, RateLimiter
from core.config import config

async def main():
    # Configuration personnalisée
    config.update({
        "timeout": 15,
        "security": {
            "verify_ssl": True,
            "check_headers": True
        },
        "rate_limit": {
            "requests_per_second": 2
        }
    })
    
    # En-têtes personnalisés
    custom_headers = {
        "User-Agent": "DNARecon Advanced Scan",
        "X-Custom-Header": "test",
        "Accept": "application/json"
    }
    
    # Liste d'URLs à analyser
    urls = [
        "https://example.com",
        "https://httpbin.org/headers",
        "https://httpbin.org/status/200"
    ]
    
    # Initialisation du rate limiter
    rate_limiter = RateLimiter(
        max_requests=config["rate_limit"]["requests_per_second"],
        time_window=1.0
    )
    
    print("[*] Démarrage de l'analyse avancée")
    
    try:
        results = []
        for url in urls:
            print(f"\n[*] Analyse de {url}")
            
            # Acquisition du rate limiter
            await rate_limiter.acquire()
            
            try:
                # Exécution de l'analyse
                result = await run(
                    url,
                    custom_headers=custom_headers,
                    is_async=True,
                    use_cache=True
                )
                results.append(result)
                
                # Affichage des résultats
                print_results(result)
                
            finally:
                rate_limiter.release()
        
        # Sauvegarde des résultats
        output_dir = Path("demo/results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "advanced_scan_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n[+] Résultats sauvegardés dans {output_file}")
        
    except Exception as e:
        print(f"[!] Erreur lors de l'analyse : {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 