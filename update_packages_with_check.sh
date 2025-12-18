#!/bin/bash
# Script to update package information weekly

set -e

# Change to script directory
cd "$(dirname "$0")"

# Log file
LOG_FILE="/tmp/lliurex-packages.log"

echo "=== $(date) ===" >> "$LOG_FILE"

# Pull latest changes
echo "Pulling latest changes..." >> "$LOG_FILE"
git pull >> "$LOG_FILE" 2>&1

# Update package information
echo "Fetching package information..." >> "$LOG_FILE"
/usr/bin/python3 fetch_packages.py >> "$LOG_FILE" 2>&1

# Check if there are actual changes in package files
if git diff --quiet packages_state.json packages_*_main.json changes_timestamps.json 2>/dev/null; then
    echo "✓ No changes detected in packages - skipping commit" >> "$LOG_FILE"
    exit 0
fi

# There are changes, commit and push
echo "✨ Changes detected - committing and pushing" >> "$LOG_FILE"
git add packages_state.json packages_state_internal.json packages_*_main.json changes_timestamps.json >> "$LOG_FILE" 2>&1
git commit -m "📦 Update packages from $(hostname)" >> "$LOG_FILE" 2>&1
git push >> "$LOG_FILE" 2>&1

echo "✅ Packages updated successfully" >> "$LOG_FILE"
