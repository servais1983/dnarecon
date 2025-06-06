#!/usr/bin/env python3
"""
Exemple d'utilisation du rate limiting avec DNARecon.
"""

import asyncio
import json
from pathlib import Path
from core.analyzer import run, print_results, RateLimiter
from core.config import config

async def main():
    # Configuration
    config.update({
        "timeout": 10,
        "rate_limit": {
            "requests_per_second": 2
        }
    })
    
    # Liste d'URLs à analyser
    urls = [
        "https://example.com",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/3"
    ]
    
    # En-têtes personnalisés
    custom_headers = {
        "User-Agent": "DNARecon Rate Limiting Demo",
        "Accept": "text/html"
    }
    
    # Initialisation du rate limiter
    rate_limiter = RateLimiter(
        max_requests=config["rate_limit"]["requests_per_second"],
        time_window=1.0
    )
    
    print("[*] Démarrage de l'analyse avec rate limiting")
    print(f"[*] Limite : {config['rate_limit']['requests_per_second']} requêtes par seconde")
    
    try:
        results = []
        for i, url in enumerate(urls, 1):
            print(f"\n[*] Requête {i}/{len(urls)} : {url}")
            
            # Acquisition du rate limiter
            await rate_limiter.acquire()
            print("[+] Rate limiter acquis")
            
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
                print("[+] Rate limiter libéré")
        
        # Sauvegarde des résultats
        output_dir = Path("demo/results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "rate_limiting_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n[+] Résultats sauvegardés dans {output_file}")
        
    except Exception as e:
        print(f"[!] Erreur lors de l'analyse : {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 