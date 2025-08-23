#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"
LOCAL_HOOKS_DIR="$REPO_ROOT/.githooks"

if [ ! -d "$GIT_HOOKS_DIR" ]; then
  echo "[ERROR] .git/hooks not found. Initialize a git repo first (git init or clone the repo)."
  exit 1
fi

echo "[INFO] Installing git hooks from $LOCAL_HOOKS_DIR to $GIT_HOOKS_DIR"
cp -v "$LOCAL_HOOKS_DIR"/* "$GIT_HOOKS_DIR"/
chmod +x "$GIT_HOOKS_DIR"/*

echo "[OK] Hooks installed."
