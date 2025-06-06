#!/usr/bin/env python3

import argparse
import asyncio
from core import analyzer, classifier, llm
from core.utils import run_script_yaml

async def main():
    parser = argparse.ArgumentParser(description="Reconnaissance comportementale (DNARecon)")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Commande analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyse une URL")
    analyze_parser.add_argument("url", help="URL à analyser")

    # Commande classify
    classify_parser = subparsers.add_parser("classify", help="Classe les résultats")
    classify_parser.add_argument("file", help="Fichier de résultats à classifier")

    # Commande llm-tag
    llm_parser = subparsers.add_parser("llm-tag", help="Analyse avec LLM")
    llm_parser.add_argument("file", help="Fichier à analyser")

    # Commande run
    run_parser = subparsers.add_parser("run", help="Exécute un scénario YAML")
    run_parser.add_argument("file", help="Fichier YAML du scénario")

    args = parser.parse_args()

    if args.command == "analyze":
        await analyzer.run(args.url, is_async=True)
    elif args.command == "classify":
        classifier.run(args.file)
    elif args.command == "llm-tag":
        llm.run(args.file)
    elif args.command == "run":
        await run_script_yaml(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())