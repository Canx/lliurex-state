#!/bin/bash
# Script to update local status only if there are changes

set -e

# Change to script directory
cd "$(dirname "$0")"

# Log file
LOG_FILE="/tmp/lliurex-status-local.log"

echo "=== $(date) ===" >> "$LOG_FILE"

# Pull latest changes
echo "Pulling latest changes..." >> "$LOG_FILE"
git pull >> "$LOG_FILE" 2>&1

# Update local status
echo "Updating local status..." >> "$LOG_FILE"
/usr/bin/python3 update_status_local.py >> "$LOG_FILE" 2>&1

# Check if there are actual changes in local_status.json
if git diff --quiet local_status.json README.md 2>/dev/null; then
    echo "✓ No changes detected in local status - skipping commit" >> "$LOG_FILE"
    exit 0
fi

# There are changes, commit and push
echo "✨ Changes detected - committing and pushing" >> "$LOG_FILE"
git add local_status.json README.md >> "$LOG_FILE" 2>&1
git commit -m "🏠 Update local status from $(hostname)" >> "$LOG_FILE" 2>&1
git push >> "$LOG_FILE" 2>&1

echo "✅ Local status updated successfully" >> "$LOG_FILE"
