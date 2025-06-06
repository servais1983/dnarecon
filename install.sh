#!/bin/bash

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Fonction pour afficher les messages
print_message() {
    echo -e "${2}[*] $1${NC}"
}

# Vérification si on est root
if [ "$EUID" -ne 0 ]; then
    print_message "Ce script doit être exécuté en tant que root (sudo)" "$RED"
    exit 1
fi

# Mise à jour du système
print_message "Mise à jour du système..." "$YELLOW"
apt update && apt upgrade -y

# Installation des dépendances système
print_message "Installation des dépendances système..." "$YELLOW"
apt install -y python3 python3-pip python3-venv python3-dev \
    build-essential libssl-dev libffi-dev \
    git curl wget nmap \
    sqlmap hydra nikto dirb \
    burpsuite

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    print_message "Python 3 n'est pas installé. Installation..." "$RED"
    apt install -y python3
fi

# Vérification de la version de Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    print_message "Python 3.8 ou supérieur est requis. Version actuelle: $PYTHON_VERSION" "$RED"
    exit 1
fi

# Création de l'environnement virtuel
print_message "Création de l'environnement virtuel..." "$YELLOW"
python3 -m venv venv

# Activation de l'environnement virtuel
print_message "Activation de l'environnement virtuel..." "$YELLOW"
source venv/bin/activate

# Mise à jour de pip
print_message "Mise à jour de pip..." "$YELLOW"
python3 -m pip install --upgrade pip

# Installation des dépendances de base
print_message "Installation des dépendances de base..." "$YELLOW"
pip install setuptools wheel

# Installation des dépendances de développement
print_message "Installation des dépendances de développement..." "$YELLOW"
pip install -r requirements-dev.txt

# Installation du projet en mode développement
print_message "Installation du projet en mode développement..." "$YELLOW"
pip install -e .

# Création du dossier de configuration
print_message "Création du dossier de configuration..." "$YELLOW"
mkdir -p ~/.dnarecon

# Configuration des permissions
print_message "Configuration des permissions..." "$YELLOW"
chmod +x dnarecon.py
chmod +x scripts/*.sh

# Vérification de l'installation
print_message "Vérification de l'installation..." "$YELLOW"
if python3 -c "import requests, yaml, dotenv, colorama, tqdm, bs4, aiohttp, pytest, setuptools" &> /dev/null; then
    print_message "Installation réussie !" "$GREEN"
    print_message "Pour utiliser DNARecon, activez d'abord l'environnement virtuel avec: source venv/bin/activate" "$GREEN"
else
    print_message "Erreur lors de l'installation des dépendances." "$RED"
    exit 1
fi

# Création d'un alias pour DNARecon
print_message "Création d'un alias pour DNARecon..." "$YELLOW"
echo "alias dnarecon='source $(pwd)/venv/bin/activate && python3 $(pwd)/dnarecon.py'" >> ~/.bashrc
source ~/.bashrc

print_message "Installation terminée ! Vous pouvez maintenant utiliser 'dnarecon' depuis n'importe quel terminal." "$GREEN"