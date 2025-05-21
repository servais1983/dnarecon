#!/usr/bin/env python3

import argparse
from core import analyzer, classifier, llm
from core.utils import run_script_yaml

def main():
    parser = argparse.ArgumentParser(prog="dnarecon", description="Reconnaissance comportementale (DNARecon)")
    subparsers = parser.add_subparsers(dest="command")

    analyze = subparsers.add_parser("analyze")
    analyze.add_argument("url")

    classify = subparsers.add_parser("classify")
    classify.add_argument("file")

    tag = subparsers.add_parser("llm-tag")
    tag.add_argument("file")

    run = subparsers.add_parser("run")
    run.add_argument("file")

    args = parser.parse_args()

    if args.command == "analyze":
        analyzer.run(args.url)
    elif args.command == "classify":
        classifier.run(args.file)
    elif args.command == "llm-tag":
        llm.run(args.file)
    elif args.command == "run":
        run_script_yaml(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()