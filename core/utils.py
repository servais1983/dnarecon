import yaml
from core import analyzer, classifier
import asyncio

async def run_script_yaml(path):
    print(f"[*] Exécution du scénario : {path}")
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    url = data.get("url", "")
    for step in data.get("steps", []):
        if step == "analyze":
            await analyzer.run(url)
        elif step == "classify":
            classifier.run("dna_results.json")
        else:
            print(f"[!] Étape inconnue : {step}")