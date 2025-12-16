#!/usr/bin/env python3
"""
Script to check if repository states have changed
Returns exit code 0 if there are changes, 1 if no changes
"""
import json
import sys
from datetime import datetime

def load_json(filename):
    """Load JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def get_repo_state(repo_info):
    """Extract relevant state information from repo info"""
    return {
        'status': repo_info.get('status'),
        'http_code': repo_info.get('http_code'),
        'last_update': repo_info.get('last_update')
    }

def main():
    # Load current history
    history = load_json('history.json')
    if not history or len(history) == 0:
        print("No history found - this is the first run")
        sys.exit(0)  # Consider first run as a change

    # Load current packages state
    packages_state = load_json('packages_state.json')
    if not packages_state:
        print("No packages_state.json found - cannot compare")
        sys.exit(0)  # Assume changes if we can't compare

    # Get the last recorded state from history
    last_entry = history[-1]

    # Compare repository states
    current_repos = packages_state.get('repos', {})
    last_repos = last_entry.get('repos', {})

    changes_detected = False
    changes = []

    for repo_name in current_repos.keys():
        current_state = get_repo_state(current_repos.get(repo_name, {}))
        last_state = get_repo_state(last_repos.get(repo_name, {}))

        # Check if status changed
        if current_state['status'] != last_state['status']:
            changes_detected = True
            changes.append(f"  - {repo_name}: status changed from '{last_state['status']}' to '{current_state['status']}'")

        # Check if last_update changed (repository was updated)
        elif current_state['last_update'] != last_state['last_update']:
            changes_detected = True
            changes.append(f"  - {repo_name}: repository updated (last_update changed)")

    # Check for new or removed repositories
    current_repos_set = set(current_repos.keys())
    last_repos_set = set(last_repos.keys())

    new_repos = current_repos_set - last_repos_set
    removed_repos = last_repos_set - current_repos_set

    if new_repos:
        changes_detected = True
        for repo in new_repos:
            changes.append(f"  - {repo}: new repository detected")

    if removed_repos:
        changes_detected = True
        for repo in removed_repos:
            changes.append(f"  - {repo}: repository removed")

    if changes_detected:
        print("✨ Changes detected:")
        for change in changes:
            print(change)
        sys.exit(0)  # Exit 0 means changes detected
    else:
        print("✓ No changes detected - states are the same")
        sys.exit(1)  # Exit 1 means no changes

if __name__ == "__main__":
    main()
