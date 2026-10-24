# MultiCompress
RAMANANTOANINA Harirojo Johan

## Présentation

MultiCompress est une application Python locale pour compresser et décompresser des fichiers au format BZip2, LZMA / XZ et 7z. Le projet est conçu comme une application pédagogique et exécutable, avec une interface en ligne de commande et une interface graphique Tkinter.

Le projet utilise les moteurs standards de Python quand ils sont suffisants (`bz2`, `lzma`) et le binaire 7z du système pour les vraies archives `.7z`.

## Objectifs

- compresser et décompresser des fichiers réels ;
- gérer les erreurs de format et de corruption ;
- sécuriser les écrans/chemins de sortie ;
- offrir une interface CLI et une interface graphique ;
- garder un code modulaire et testable.

## Prérequis

- Python 3.10+
- `pytest` pour les tests
- `tk` pour la GUI
- `p7zip` pour les archives 7z sous Arch Linux

## Installation sur Arch Linux

### 1) Créer un environnement virtuel

```bash
cd /home/fytahx/Projects/Multicompress
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

### 2) Installer les dépendances système

```bash
sudo pacman -S p7zip tk
```

### 3) Vérifier l’installation

```bash
7z
multicompress --help
```

## Lancement

### Interface CLI

```bash
cd /home/fytahx/Projects/Multicompress
. .venv/bin/activate
multicompress --help
```

### Interface graphique

```bash
cd /home/fytahx/Projects/Multicompress
. .venv/bin/activate
multicompress --gui
```

ou

```bash
multicompress-gui
```

## Utilisation

### BZip2

```bash
multicompress bzip2 compress document.txt
multicompress bzip2 decompress document.txt.bz2
multicompress bzip2 test document.txt.bz2
```

### LZMA / XZ

```bash
multicompress lzma compress fichier.bin --format lzma
multicompress lzma compress fichier.bin --format xz
multicompress lzma decompress fichier.bin.lzma
multicompress lzma test fichier.bin.xz
```

### 7z

```bash
multicompress 7z create archive.7z dossier/
multicompress 7z extract archive.7z --output ./restauration
multicompress 7z list archive.7z
multicompress 7z test archive.7z
```

## Architecture du projet

```text
src/
  multicompress/
    __init__.py
    __main__.py
    cli.py
    gui.py
    config.py
    exceptions.py
    file_utils.py
    statistics.py
    engines/
      base.py
      bzip2_engine.py
      lzma_engine.py
      sevenzip_engine.py
    services/
      compression_service.py
      archive_service.py
```

## Formats pris en charge

### BZip2

- compression standard ;
- décompression sécurisée ;
- détection des flux corrompus ;
- refus d’écraser un fichier existant sans autorisation explicite.

### LZMA / XZ / LZMA2

- `lzma` : flux LZMA standard ;
- `xz` : conteneur XZ ;
- `lzma2` : format largement utilisé dans les archives modernes.

### 7z

- création de vraies archives `.7z` via le binaire `7z` ;
- liste du contenu ;
- extraction ;
- test d’intégrité de l’archive.

## Sécurité

Le projet refuse de remplacer silencieusement un fichier existant et protège les opérations de sortie. Les archives sont traitées avec des contrôles de base sur les chemins et les erreurs système.

## Tests

Pour lancer la suite de tests :

```bash
cd /home/fytahx/Projects/Multicompress
. .venv/bin/activate
python -m pytest -q
```

## Statut vérifié

La version actuelle a été testée avec succès :

```text
15 passed, 1 skipped in 0.62s
```

## Désinstallation

```bash
cd /home/fytahx/Projects/Multicompress
rm -rf .venv
```

## Licence

Projet académique.
