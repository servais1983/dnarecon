#!/bin/bash
echo "[*] Installation de DNARecon sur Kali..."

sudo apt update
sudo apt install -y python3 python3-pip
pip3 install -r requirements.txt

echo "[+] DNARecon installé. Lancement par : python3 dnarecon.py run scripts/test_web_behavior.yaml"