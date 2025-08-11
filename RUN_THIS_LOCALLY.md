# Fix Black Formatting for CI

The CI is failing because 294 files need reformatting. To fix this:

## Option 1: Use the provided script
```bash
./fix_formatting.sh
```

## Option 2: Run manually
```bash
# Install Black if not already installed
pip install black

# Format all Python files in electrum/
black --line-length=100 electrum/

# Commit the changes
git add -A
git commit -m "style: apply Black formatting to all Python files

- Applied Black formatter with 100 char line length
- Reformatted 294 files to match style requirements
- Fixes CI formatting check"

# Push to GitHub
git push origin master
```

After running these commands, the CI should pass the formatting check.
