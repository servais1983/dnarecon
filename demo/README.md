# Exemples de démonstration DNARecon

Ce dossier contient des exemples d'utilisation de DNARecon pour différents scénarios.

## Structure

- `basic_scan.py` : Exemple basique d'analyse d'une URL
- `advanced_scan.py` : Exemple avancé avec configuration personnalisée
- `batch_scan.py` : Exemple d'analyse en lot de plusieurs URLs
- `security_headers.py` : Exemple de vérification des en-têtes de sécurité
- `rate_limiting.py` : Exemple d'utilisation du rate limiting
- `cache_usage.py` : Exemple d'utilisation du cache
- `scenarios/` : Dossier contenant des scénarios YAML prédéfinis

## Utilisation

1. Assurez-vous d'avoir installé DNARecon :
```bash
pip install -e .
```

2. Exécutez les exemples :
```bash
python demo/basic_scan.py
```

## Scénarios disponibles

### Scénario basique
```yaml
# scenarios/basic.yaml
url: https://example.com
headers:
  User-Agent: DNARecon Demo
cache: true
```

### Scénario de sécurité
```yaml
# scenarios/security.yaml
url: https://example.com
headers:
  User-Agent: DNARecon Security Scan
security:
  verify_ssl: true
  check_headers: true
```

### Scénario de performance
```yaml
# scenarios/performance.yaml
url: https://example.com
rate_limit:
  requests_per_second: 2
cache:
  enabled: true
  ttl: 300
```

## Notes

- Les exemples utilisent des URLs de test. Remplacez-les par vos propres URLs.
- Certains exemples nécessitent des permissions spéciales ou des configurations spécifiques.
- Les résultats sont sauvegardés dans le dossier `demo/results/`. 