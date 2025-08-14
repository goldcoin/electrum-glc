#!/bin/bash
# Script to fix Black formatting issues for CI

echo "Installing Black formatter..."
pip install black

echo "Running Black formatter on electrum/ directory..."
black --line-length=100 electrum/

echo "Checking if any files were modified..."
if git diff --quiet; then
    echo "No files were modified. Code is already formatted correctly."
else
    echo "Files were reformatted. Please review and commit the changes."
    git status --short
fi

echo "Done! Now you can commit and push the changes."