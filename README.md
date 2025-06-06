# DNARecon – Outil de Reconnaissance Comportementale

Outil CLI professionnel pour l'analyse et la reconnaissance comportementale des applications web.

## 🌟 Fonctionnalités

- **Analyse de sécurité** :
  - Vérification des en-têtes de sécurité
  - Détection des vulnérabilités courantes
  - Analyse des réponses HTTP
  - Validation SSL/TLS

- **Performance** :
  - Requêtes asynchrones
  - Système de cache intégré
  - Rate limiting configurable
  - Analyse en lot

- **Configuration** :
  - Scénarios YAML personnalisables
  - En-têtes HTTP configurables
  - Timeouts ajustables
  - Options de sécurité flexibles

## 🛠️ Installation

```bash
# Cloner le repository
git clone https://github.com/servais1983/dnarecon.git
cd dnarecon

# Installer les dépendances
pip install -e .
```

## 🚀 Utilisation

### Analyse basique
```bash
python demo/basic_scan.py
```

### Analyse en lot
```bash
python demo/batch_scan.py
```

### Vérification des en-têtes de sécurité
```bash
python demo/security_headers.py
```

### Utilisation du rate limiting
```bash
python demo/rate_limiting.py
```

### Exécution d'un scénario YAML
```bash
python demo/run_scenario.py demo/scenarios/security.yaml
```

## 📁 Structure du projet

```
dnarecon/
├── core/               # Modules principaux
│   ├── analyzer.py    # Analyse des URLs
│   ├── classifier.py  # Classification des résultats
│   ├── config.py      # Configuration
│   └── llm.py         # Intégration LLM
├── demo/              # Exemples d'utilisation
│   ├── basic_scan.py
│   ├── batch_scan.py
│   ├── security_headers.py
│   ├── rate_limiting.py
│   └── scenarios/     # Scénarios YAML
├── tests/             # Tests unitaires
└── scripts/           # Scripts utilitaires
```

## 📋 Scénarios disponibles

### Scénario basique
```yaml
url: https://example.com
headers:
  User-Agent: DNARecon Demo
cache: true
timeout: 30
```

### Scénario de sécurité
```yaml
url: https://example.com
security:
  verify_ssl: true
  check_headers: true
  strict_headers: true
```

### Scénario de performance
```yaml
url: https://example.com
performance:
  concurrent_requests: 5
  timeout: 10
rate_limit:
  requests_per_second: 5
```

## 🔧 Configuration

L'outil peut être configuré via :
- Fichiers YAML
- Variables d'environnement
- Arguments en ligne de commande
- API Python

## 🧪 Tests

```bash
# Exécuter tous les tests
python -m pytest tests/ -v

# Exécuter les tests avec couverture
python -m pytest tests/ --cov=core
```

## 📊 Métriques

- 51 tests unitaires
- Couverture de code > 90%
- Temps de réponse < 100ms par requête
- Support de 1000+ URLs en lot

## 🔒 Sécurité

- Validation des entrées
- Protection contre les attaques
- Gestion sécurisée des configurations
- Rate limiting intégré

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

## 📝 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation
- Contacter l'équipe de support