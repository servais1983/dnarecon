import json

def run(file):
    print(f"[*] Classification des réponses depuis {file}")
    with open(file, "r") as f:
        data = json.load(f)

    for entry in data:
        status = entry["status"]
        body = entry["body"]
        attack = entry["attack"]

        if "alert(1)" in body or "syntax" in body.lower():
            print(f"[!] Comportement VULNÉRABLE pour attaque {attack} → {entry['url']}")
        elif status == 403 or "access denied" in body.lower():
            print(f"[+] Comportement STRICT pour attaque {attack} → {entry['url']}")
        else:
            print(f"[~] Comportement FLEXIBLE pour attaque {attack} → {entry['url']}")