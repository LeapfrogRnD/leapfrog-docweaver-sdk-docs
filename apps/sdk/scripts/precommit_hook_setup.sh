#!/usr/bin/env bash
# Cross-platform pre-commit hook setup
# Works on Linux, macOS, and Windows (Git Bash / WSL / PowerShell)

set -e

echo "Setting up pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit >/dev/null 2>&1; then
    echo "pre-commit is not installed."
    echo "Install it first using: pip install pre-commit"
    exit 1
fi

# Install default pre-commit hooks
pre-commit install
echo "Default pre-commit hooks installed."

# Install commit-msg hook
pre-commit install --hook-type commit-msg
echo "commit-msg hook installed."

# Optional: run all hooks once to verify
echo " Running pre-commit hooks on all files to verify..."
pre-commit run --all-files --verbose || true

echo " All hooks are set up successfully!"
