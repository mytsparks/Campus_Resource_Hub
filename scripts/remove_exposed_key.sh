#!/usr/bin/env bash
set -euo pipefail

# Usage: bash scripts/remove_exposed_key.sh "PASTE_EXPOSED_KEY_HERE"
# Requires: git-filter-repo OR BFG Repo Cleaner (Java)

EXPOSED_KEY="${1:-}"
if [[ -z "$EXPOSED_KEY" ]]; then
  echo "Error: Provide the exposed key as the first argument."
  echo "Example: bash scripts/remove_exposed_key.sh AIzaSyXXXX"
  exit 1
fi

echo "==> Creating replacement file"
TMPFILE=$(mktemp)
echo "$EXPOSED_KEY==>REMOVED_API_KEY" > "$TMPFILE"

if command -v git-filter-repo >/dev/null 2>&1; then
  echo "==> Using git-filter-repo to scrub history"
  git filter-repo --replace-text "$TMPFILE"
else
  echo "git-filter-repo not found. Falling back to BFG instructions:"
  echo "1) Download BFG: https://rtyley.github.io/bfg-repo-cleaner/"
  echo "2) Create keys.txt containing the exposed key"
  echo "3) Run: java -jar bfg.jar --replace-text keys.txt"
  echo "4) Then clean: git reflog expire --expire=now --all && git gc --prune=now --aggressive"
fi

echo "==> Done. Force push required if remote exists:"
echo "    git push --force"


