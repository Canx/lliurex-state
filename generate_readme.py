#!/usr/bin/env python3
"""
Script to generate README.md from status files
This script reads both history.json (external checks) and local_status.json (local checks)
and generates a unified README.md
"""
import json
import subprocess
import os
from typing import Dict, Optional

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

def load_external_status() -> Optional[Dict]:
    """Load the latest external status from history.json"""
    try:
        with open("history.json", "r") as f:
            history = json.load(f)
            if history:
                return history[-1]  # Return most recent entry
    except FileNotFoundError:
        pass
    return None

def load_local_status() -> Optional[Dict]:
    """Load the latest local status from local_status.json"""
    try:
        with open("local_status.json", "r") as f:
            history = json.load(f)
            if history:
                return history[-1]  # Return most recent entry
    except FileNotFoundError:
        pass
    return None

def generate_readme() -> str:
    """Generate README.md content from status files"""
    github_repo = get_github_repo()
    github_user = github_repo.split('/')[0]
    github_project = github_repo.split('/')[1]

    external_status = load_external_status()
    local_status = load_local_status()

    readme = f"""# LliureX Repository Status

[![Check Status](https://github.com/{github_repo}/actions/workflows/check-status.yml/badge.svg)](https://github.com/{github_repo}/actions/workflows/check-status.yml)
[![Update Packages](https://github.com/{github_repo}/actions/workflows/update-packages.yml/badge.svg)](https://github.com/{github_repo}/actions/workflows/update-packages.yml)

Este repositorio monitorea automáticamente el estado de los repositorios de LliureX para diferentes versiones de Ubuntu.

**🌐 [Ver página con información detallada de paquetes](https://{github_user}.github.io/{github_project}/)**

## 📊 Estado Actual

"""

    # Add external status section
    if external_status:
        readme += f"""### 🌍 Estado Externo (GitHub Actions)

**Última actualización:** {external_status['timestamp']} UTC

"""
        readme += "| Versión Ubuntu | Estado | Última Actualización Repo | URL |\n"
        readme += "|----------------|--------|---------------------------|-----|\n"

        for repo_name, info in sorted(external_status["repos"].items()):
            status_emoji = "✅" if info["status"] == "online" else "❌"
            version_name = get_version_name(repo_name)
            url = info.get("url", "")
            last_update = info.get("last_update", "N/A")

            readme += f"| Ubuntu {version_name} ({repo_name}) | {status_emoji} {info['status']} | {last_update} | [Link]({url}) |\n"
    else:
        readme += """### 🌍 Estado Externo (GitHub Actions)

_No hay datos de verificación externa disponibles._

"""

    # Add local status section
    if local_status:
        readme += f"""

### 🏠 Estado Local (Red LliureX)

**Última actualización:** {local_status['timestamp']} UTC
**Servidor:** {local_status.get('hostname', 'N/A')}

"""
        readme += "| Versión Ubuntu | Estado | Última Actualización Repo | URL |\n"
        readme += "|----------------|--------|---------------------------|-----|\n"

        for repo_name, info in sorted(local_status["repos"].items()):
            status_emoji = "✅" if info["status"] == "online" else "❌"
            version_name = get_version_name(repo_name)
            url = info.get("url", "")
            last_update = info.get("last_update", "N/A")

            readme += f"| Ubuntu {version_name} ({repo_name}) | {status_emoji} {info['status']} | {last_update} | [Link]({url}) |\n"
    else:
        readme += """

### 🏠 Estado Local (Red LliureX)

_No hay datos de verificación local disponibles. Ejecuta `update_status_local.py` desde la red local para obtener esta información._

"""

    readme += """

## 📦 Repositorios de LliureX

LliureX mantiene repositorios para diferentes versiones LTS de Ubuntu:

- **Focal (20.04 LTS)**: Versión anterior de soporte extendido
- **Jammy (22.04 LTS)**: Versión LTS actual
- **Noble (24.04 LTS)**: Versión LTS más reciente

Cada repositorio contiene los paquetes específicos de LliureX adaptados para esa versión de Ubuntu.

## 🔄 Actualización Automática

### Estado de Repositorios
Se verifica cada hora mediante GitHub Actions, comprobando el estado de disponibilidad y última actualización de los repositorios desde fuera de la red LliureX.

### Información de Paquetes
Se actualiza semanalmente (domingos a las 02:00 UTC) mediante GitHub Actions, generando páginas HTML con información detallada de todos los paquetes disponibles.

### Estado Local
Para monitorizar el estado desde la red local, ejecuta `update_status_local.py` manualmente o configura un cron job. El README se regenera automáticamente cada vez que se actualiza cualquiera de los estados.

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

def main():
    print("📝 Generating README.md from status files...")

    readme_content = generate_readme()

    with open("README.md", "w") as f:
        f.write(readme_content)

    print("✅ README.md generated successfully!")

if __name__ == "__main__":
    main()
