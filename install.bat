@echo off
echo [*] Installation de DNARecon...

REM Vérification de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python n'est pas installé. Veuillez l'installer d'abord.
    exit /b 1
)

REM Création de l'environnement virtuel
echo [*] Création de l'environnement virtuel...
python -m venv venv

REM Activation de l'environnement virtuel
echo [*] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Mise à jour de pip
echo [*] Mise à jour de pip...
python -m pip install --upgrade pip

REM Installation des dépendances de base
echo [*] Installation des dépendances de base...
pip install setuptools wheel

REM Installation des dépendances de développement
echo [*] Installation des dépendances de développement...
pip install -r requirements-dev.txt

REM Installation du projet en mode développement
echo [*] Installation du projet en mode développement...
pip install -e .

REM Création du dossier de configuration
echo [*] Création du dossier de configuration...
if not exist "%USERPROFILE%\.dnarecon" mkdir "%USERPROFILE%\.dnarecon"

REM Vérification de l'installation
echo [*] Vérification de l'installation...
python -c "import requests, yaml, dotenv, colorama, tqdm, bs4, aiohttp, pytest, setuptools" 2>nul
if errorlevel 1 (
    echo [ERROR] Erreur lors de l'installation des dépendances.
    exit /b 1
) else (
    echo [+] Installation réussie !
    echo [+] Pour utiliser DNARecon, activez d'abord l'environnement virtuel avec: venv\Scripts\activate.bat
)

REM Rendre le script principal exécutable
attrib +x dnarecon.py 