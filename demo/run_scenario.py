#!/usr/bin/env python3
"""
Script pour exécuter les scénarios YAML de DNARecon.
"""

import asyncio
import json
import yaml
from pathlib import Path
from core.analyzer import run, print_results
from core.config import config

async def run_scenario(scenario_file: str):
    """Exécute un scénario YAML."""
    # Lecture du scénario
    with open(scenario_file, 'r') as f:
        scenario = yaml.safe_load(f)
    
    # Configuration
    if 'timeout' in scenario:
        config['timeout'] = scenario['timeout']
    if 'security' in scenario:
        config['security'].update(scenario['security'])
    if 'rate_limit' in scenario:
        config['rate_limit'].update(scenario['rate_limit'])
    
    # En-têtes personnalisés
    custom_headers = scenario.get('headers', {})
    
    print(f"[*] Exécution du scénario : {scenario_file}")
    print(f"[*] URL cible : {scenario['url']}")
    
    try:
        # Exécution de l'analyse
        results = await run(
            scenario['url'],
            custom_headers=custom_headers,
            is_async=True,
            use_cache=scenario.get('cache', True)
        )
        
        # Affichage des résultats
        print("\n[*] Résultats de l'analyse :")
        print_results(results)
        
        # Sauvegarde des résultats
        output_dir = Path("demo/results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        scenario_name = Path(scenario_file).stem
        output_file = output_dir / f"{scenario_name}_results.json"
        
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n[+] Résultats sauvegardés dans {output_file}")
        
    except Exception as e:
        print(f"[!] Erreur lors de l'analyse : {str(e)}")

async def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Exécute un scénario DNARecon")
    parser.add_argument("scenario", help="Chemin vers le fichier de scénario YAML")
    args = parser.parse_args()
    
    await run_scenario(args.scenario)

if __name__ == "__main__":
    asyncio.run(main()) 