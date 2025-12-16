#!/usr/bin/env python3
"""
Script to fetch LliureX repository status and update README.md
"""
import requests
from datetime import datetime
from typing import Dict
import json
import re
import subprocess
import os

LLIUREX_BASE_URL = "http://lliurex.net"
UBUNTU_VERSIONS = [
    "focal",    # Ubuntu 20.04 LTS
    "jammy",    # Ubuntu 22.04 LTS
    "noble",    # Ubuntu 24.04 LTS
]

def fetch_repo_info(version: str) -> Dict:
    """Fetch information from a specific Ubuntu version repository"""
    url = f"{LLIUREX_BASE_URL}/{version}/"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            content = response.text

            # Try to find Release file to get more info
            release_url = f"{url}dists/{version}/Release"
            release_response = requests.get(release_url, timeout=10)

            packages_count = "N/A"
            last_update = "N/A"

            if release_response.status_code == 200:
                release_content = release_response.text
                # Extract date from Release file
                date_match = re.search(r'Date:\s*(.+)', release_content)
                if date_match:
                    last_update = date_match.group(1).strip()

                # Count packages from Packages files
                packages_match = re.findall(r'(\d+)\s+main/binary', release_content)
                if packages_match:
                    packages_count = sum(int(x) for x in packages_match)

            return {
                "status": "online",
                "url": url,
                "last_update": last_update,
                "packages": packages_count,
                "http_code": 200
            }
        else:
            return {
                "status": "error",
                "url": url,
                "http_code": response.status_code,
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "offline",
            "url": url,
            "error": str(e)
        }

def fetch_all_repos() -> Dict:
    """Fetch information from all repositories"""
    repo_data = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "repos": {}
    }

    for version in UBUNTU_VERSIONS:
        print(f"Checking {version}...")
        repo_data["repos"][version] = fetch_repo_info(version)

    return repo_data

def get_version_name(codename: str) -> str:
    """Get Ubuntu version number from codename"""
    versions = {
        "focal": "20.04 LTS",
        "jammy": "22.04 LTS",
        "noble": "24.04 LTS"
    }
    return versions.get(codename, codename)

def get_github_repo() -> str:
    """Get GitHub repository from git remote or environment variable"""
    # Try from environment (GitHub Actions)
    github_repo = os.environ.get('GITHUB_REPOSITORY')
    if github_repo:
        return github_repo

    # Try from git remote
    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()

        # Parse GitHub URL
        if 'github.com' in remote_url:
            # Handle both HTTPS and SSH URLs
            if remote_url.startswith('https://'):
                # https://github.com/user/repo.git
                parts = remote_url.replace('https://github.com/', '').replace('.git', '')
            elif remote_url.startswith('git@'):
                # git@github.com:user/repo.git
                parts = remote_url.replace('git@github.com:', '').replace('.git', '')
            else:
                parts = None

            if parts:
                return parts
    except:
        pass

    # Fallback
    return "Canx/lliurex-state"

def generate_readme(repo_data: Dict) -> str:
    """Generate README.md content"""
    github_repo = get_github_repo()

    readme = f"""# LliureX Repository Status

[![Update Status](https://github.com/{github_repo}/actions/workflows/update-status.yml/badge.svg)](https://github.com/{github_repo}/actions/workflows/update-status.yml)

Este repositorio monitorea automáticamente el estado de los repositorios de LliureX para diferentes versiones de Ubuntu.

## 📊 Estado Actual

**Última actualización:** {repo_data['timestamp']} UTC

"""

    # Add status table
    readme += "| Versión Ubuntu | Estado | Última Actualización Repo | URL |\n"
    readme += "|----------------|--------|---------------------------|-----|\n"

    for repo_name, info in sorted(repo_data["repos"].items()):
        status_emoji = "✅" if info["status"] == "online" else "❌"
        version_name = get_version_name(repo_name)
        url = info.get("url", "")
        last_update = info.get("last_update", "N/A")

        readme += f"| Ubuntu {version_name} ({repo_name}) | {status_emoji} {info['status']} | {last_update} | [Link]({url}) |\n"

    readme += """

## 📦 Repositorios de LliureX

LliureX mantiene repositorios para diferentes versiones LTS de Ubuntu:

- **Focal (20.04 LTS)**: Versión anterior de soporte extendido
- **Jammy (22.04 LTS)**: Versión LTS actual
- **Noble (24.04 LTS)**: Versión LTS más reciente

Cada repositorio contiene los paquetes específicos de LliureX adaptados para esa versión de Ubuntu.

## 🔄 Actualización Automática

Este repositorio se actualiza automáticamente cada día a las 00:00 UTC mediante GitHub Actions.

## 📖 Acerca de LliureX

LliureX es una distribución Linux educativa desarrollada por la Generalitat Valenciana, basada en Ubuntu y diseñada específicamente para el ámbito educativo.

- **Web oficial:** https://lliurex.net/
- **Wiki:** https://wiki.lliurex.net/
- **Portal educativo:** https://portal.edu.gva.es/

## 🔗 Enlaces Útiles

- [Repositorio Principal](https://lliurex.net/)
- [Documentación](https://wiki.lliurex.net/)
- [Descargas](https://lliurex.net/descargas/)

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

*Generado automáticamente por GitHub Actions*
"""

    return readme

def save_history(repo_data: Dict):
    """Save historical data"""
    try:
        with open("history.json", "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    history.append(repo_data)

    # Keep only last 30 days
    if len(history) > 30:
        history = history[-30:]

    with open("history.json", "w") as f:
        json.dump(history, f, indent=2)

def main():
    print("🔍 Fetching LliureX repository status...")
    repo_data = fetch_all_repos()

    print("\n📝 Generating README.md...")
    readme_content = generate_readme(repo_data)

    with open("README.md", "w") as f:
        f.write(readme_content)

    print("💾 Saving historical data...")
    save_history(repo_data)

    print("\n✅ Status update completed!")

    # Print summary
    online_count = sum(1 for r in repo_data["repos"].values() if r["status"] == "online")
    total_count = len(repo_data["repos"])
    print(f"\n📊 Summary: {online_count}/{total_count} repositories online")

    for repo_name, info in sorted(repo_data["repos"].items()):
        status = "✅" if info["status"] == "online" else "❌"
        print(f"   {status} {repo_name}: {info['status']}")

if __name__ == "__main__":
    main()
