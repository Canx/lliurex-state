#!/usr/bin/env python3
"""
Script to fetch LliureX repository status from external (GitHub Actions)
and update history.json
"""
import requests
from datetime import datetime
from typing import Dict
import json
import re
import subprocess
import os
import sys

LLIUREX_BASE_URL = "http://lliurex.net"
UBUNTU_VERSIONS = [
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
        "source": "github-actions",
        "repos": {}
    }

    for version in UBUNTU_VERSIONS:
        print(f"Checking {version}...")
        repo_data["repos"][version] = fetch_repo_info(version)

    return repo_data

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

    # Save to Firebase
    import firebase_config
    # We push the single new entry, not the whole history array (to act as a log)
    # But wait, the frontend might want the last X entries.
    # If we use push(), we get unique IDs.
    # Let's also update a 'latest_status' node for easy access.
    firebase_config.push_to_firebase('history', repo_data)
    firebase_config.save_to_firebase('latest_status', repo_data)

def main():
    print("🔍 Fetching LliureX repository status (external)...")
    repo_data = fetch_all_repos()

    print("💾 Saving external status to history.json...")
    save_history(repo_data)

    print("📝 Regenerating README.md...")
    subprocess.run([sys.executable, "generate_readme.py"], check=True)

    print("\n✅ External status update completed!")

    # Print summary
    online_count = sum(1 for r in repo_data["repos"].values() if r["status"] == "online")
    total_count = len(repo_data["repos"])
    print(f"\n📊 Summary: {online_count}/{total_count} repositories online")

    for repo_name, info in sorted(repo_data["repos"].items()):
        status = "✅" if info["status"] == "online" else "❌"
        print(f"   {status} {repo_name}: {info['status']}")

if __name__ == "__main__":
    main()
