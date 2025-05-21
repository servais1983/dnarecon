# DNARecon – Behavioral Recon CLI

Outil CLI pour observer les réactions d'une application à différents patterns offensifs.

## ⚙️ Modules

- `analyze <url>` : Envoie des requêtes mutées (XSS, SQLi, IDOR)
- `classify <json>` : Classe les comportements (strict, flexible, vulnérable)
- `run <yaml>` : Scénario complet
- `llm-tag <json>` : Annotation automatique (optionnelle)

## 🛠️ Installation

```bash
chmod +x install.sh
./install.sh
```

## 🚀 Exemple

```bash
python3 dnarecon.py run scripts/test_web_behavior.yaml
```