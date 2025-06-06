#!/usr/bin/env python3
"""
Exemple de vérification des en-têtes de sécurité avec DNARecon.
"""

import asyncio
import json
from pathlib import Path
from core.analyzer import run, print_results
from core.config import config

async def main():
    # Configuration de sécurité stricte
    config.update({
        "security": {
            "verify_ssl": True,
            "check_headers": True,
            "strict_headers": True,
            "check_csp": True,
            "check_hsts": True,
            "check_xss_protection": True,
            "check_frame_options": True,
            "check_content_type": True
        },
        "timeout": 30
    })
    
    # Liste d'URLs à analyser
    urls = [
        "https://example.com",
        "https://httpbin.org/headers",
        "https://httpbin.org/response-headers"
    ]
    
    # En-têtes personnalisés
    custom_headers = {
        "User-Agent": "DNARecon Security Headers Scan",
        "Accept": "text/html"
    }
    
    print("[*] Démarrage de la vérification des en-têtes de sécurité")
    
    try:
        results = []
        for url in urls:
            print(f"\n[*] Analyse de {url}")
            
            # Exécution de l'analyse
            result = await run(
                url,
                custom_headers=custom_headers,
                is_async=True,
                use_cache=False  # Désactive le cache pour les tests de sécurité
            )
            results.append(result)
            
            # Affichage des résultats
            print_results(result)
            
            # Vérification spécifique des en-têtes de sécurité
            if "headers" in result:
                headers = result["headers"]
                print("\n[*] Vérification des en-têtes de sécurité :")
                
                security_headers = {
                    "Content-Security-Policy": "CSP",
                    "Strict-Transport-Security": "HSTS",
                    "X-XSS-Protection": "XSS Protection",
                    "X-Frame-Options": "Frame Options",
                    "X-Content-Type-Options": "Content Type Options"
                }
                
                for header, name in security_headers.items():
                    if header in headers:
                        print(f"[+] {name} : Présent ({headers[header]})")
                    else:
                        print(f"[-] {name} : Absent")
        
        # Sauvegarde des résultats
        output_dir = Path("demo/results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "security_headers_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n[+] Résultats sauvegardés dans {output_file}")
        
    except Exception as e:
        print(f"[!] Erreur lors de l'analyse : {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 