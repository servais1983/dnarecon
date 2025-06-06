#!/usr/bin/env python3
"""
Exemple d'analyse en lot de plusieurs URLs avec DNARecon.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from core.analyzer import run, print_results
from core.config import config

async def analyze_url(url: str, custom_headers: Optional[dict] = None) -> dict:
    """Analyse une URL et retourne les résultats."""
    print(f"\n[*] Analyse de {url}")
    start_time = datetime.now()
    
    try:
        results = await run(
            url,
            custom_headers=custom_headers,
            is_async=True,
            use_cache=True
        )
        
        # Ajout des métadonnées
        results["metadata"] = {
            "url": url,
            "analysis_time": datetime.now().isoformat(),
            "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
            "success": True
        }
        
        print_results(results)
        return results
        
    except Exception as e:
        error_result = {
            "url": url,
            "error": str(e),
            "metadata": {
                "analysis_time": datetime.now().isoformat(),
                "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "success": False
            }
        }
        print(f"[!] Erreur lors de l'analyse de {url}: {str(e)}")
        return error_result

def print_summary(results: List[Dict]) -> None:
    """Affiche un résumé des résultats de l'analyse."""
    total = len(results)
    success = sum(1 for result in results if result.get("metadata", {}).get("success", False))
    failed = total - success
    
    print("\n[*] Résumé de l'analyse en lot :")
    print(f"    Total des URLs : {total}")
    print(f"    Analyses réussies : {success}")
    print(f"    Analyses échouées : {failed}")
    
    if success > 0:
        avg_duration = sum(result.get("metadata", {}).get("duration_ms", 0) for result in results if result.get("metadata", {}).get("success", False)) / success
        print(f"    Durée moyenne : {avg_duration:.2f} ms")
    
    print("\n[*] Détails des erreurs :")
    for result in results:
        if not result.get("metadata", {}).get("success", False):
            print(f"    - {result['url']} : {result['error']}")

async def main():
    # Configuration
    config.update({
        "timeout": 10,
        "security": {
            "verify_ssl": True,
            "check_headers": True
        }
    })
    
    # Liste d'URLs à analyser
    urls = [
        "https://example.com",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404",
        "https://httpbin.org/status/500",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2"
    ]
    
    # En-têtes personnalisés
    custom_headers = {
        "User-Agent": "DNARecon Batch Scan",
        "Accept": "text/html"
    }
    
    print("[*] Démarrage de l'analyse en lot")
    print(f"[*] Nombre d'URLs à analyser : {len(urls)}")
    
    start_time = datetime.now()
    
    # Analyse concurrente des URLs
    tasks = [analyze_url(url, custom_headers) for url in urls]
    results = await asyncio.gather(*tasks)
    
    # Calcul de la durée totale
    total_duration = (datetime.now() - start_time).total_seconds()
    
    # Affichage du résumé
    print_summary(results)
    print(f"\n[*] Durée totale de l'analyse : {total_duration:.2f} secondes")
    
    # Sauvegarde des résultats
    output_dir = Path("demo/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "batch_scan_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Résultats sauvegardés dans {output_file}")

if __name__ == "__main__":
    asyncio.run(main()) 