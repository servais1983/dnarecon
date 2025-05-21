import requests
import json

MUTATIONS = [
    ("xss", "<script>alert(1)</script>"),
    ("sqli", "' OR '1'='1"),
    ("idor", "user_id=1", "user_id=2"),
]

def run(url):
    print(f"[*] Analyse de comportement vers : {url}")
    results = []

    for attack in MUTATIONS:
        if attack[0] == "idor":
            payloads = [attack[1], attack[2]]
        else:
            payloads = [f"?input={attack[1]}"]

        for p in payloads:
            try:
                full_url = url + p
                res = requests.get(full_url, timeout=3)
                results.append({
                    "url": full_url,
                    "status": res.status_code,
                    "body": res.text[:300],
                    "attack": attack[0]
                })
            except Exception as e:
                results.append({
                    "url": url + p,
                    "status": "ERROR",
                    "body": str(e),
                    "attack": attack[0]
                })

    with open("dna_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("[+] Résultats enregistrés dans dna_results.json")