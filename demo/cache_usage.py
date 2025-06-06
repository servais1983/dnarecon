#!/usr/bin/env python3
"""
Exemple d'utilisation du cache avec DNARecon.
"""

import asyncio
import json
from pathlib import Path
from core.analyzer import run, print_results
from core.config import config

async def main():
    # Configuration du cache
    config.update({
        "cache": {
            "enabled": True,
            "ttl": 300,  # 5 minutes
            "max_size": 1000
        },
        "timeout": 10
    })
    
    # URL à analyser
    url = "https://example.com"
    
    # En-têtes personnalisés
    custom_headers = {
        "User-Agent": "DNARecon Cache Demo",
        "Accept": "text/html"
    }
    
    print("[*] Démarrage de l'analyse avec cache")
    print(f"[*] TTL du cache : {config['cache']['ttl']} secondes")
    
    try:
        results = []
        
        # Premier appel (sans cache)
        print("\n[*] Premier appel (sans cache)")
        result1 = await run(
            url,
            custom_headers=custom_headers,
            is_async=True,
            use_cache=True
        )
        results.append({"call": "first", "result": result1})
        print_results(result1)
        
        # Deuxième appel (avec cache)
        print("\n[*] Deuxième appel (avec cache)")
        result2 = await run(
            url,
            custom_headers=custom_headers,
            is_async=True,
            use_cache=True
        )
        results.append({"call": "second", "result": result2})
        print_results(result2)
        
        # Troisième appel (sans cache)
        print("\n[*] Troisième appel (sans cache)")
        result3 = await run(
            url,
            custom_headers=custom_headers,
            is_async=True,
            use_cache=False
        )
        results.append({"call": "third", "result": result3})
        print_results(result3)
        
        # Sauvegarde des résultats
        output_dir = Path("demo/results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "cache_usage_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n[+] Résultats sauvegardés dans {output_file}")
        
    except Exception as e:
        print(f"[!] Erreur lors de l'analyse : {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 