#!/usr/bin/env python3
"""
Exemple basique d'utilisation de DNARecon.
Analyse une URL simple et affiche les résultats.
"""

import asyncio
import json
from pathlib import Path
from core.analyzer import run, print_results

async def main():
    # URL à analyser
    url = "https://example.com"
    
    print(f"[*] Démarrage de l'analyse de {url}")
    
    try:
        # Exécution de l'analyse
        results = await run(url, is_async=True)
        
        # Affichage des résultats
        print("\n[*] Résultats de l'analyse :")
        print_results(results)
        
        # Sauvegarde des résultats
        output_dir = Path("demo/results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "basic_scan_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n[+] Résultats sauvegardés dans {output_file}")
        
    except Exception as e:
        print(f"[!] Erreur lors de l'analyse : {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 