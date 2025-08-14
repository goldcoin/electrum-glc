# Goldcoin Electrum Development Makefile
# Run 'make help' for a list of available commands

.PHONY: help install dev-install test lint format type-check clean pre-commit

# Default target
help:
	@echo "Goldcoin Electrum Development Commands:"
	@echo ""
	@echo "  make install        - Install Electrum with base dependencies"
	@echo "  make dev-install    - Install Electrum with all development tools"
	@echo "  make test          - Run all tests"
	@echo "  make lint          - Run all linters (ruff, flake8, bandit)"
	@echo "  make format        - Format code with black and isort"
	@echo "  make type-check    - Run mypy type checking"
	@echo "  make clean         - Remove build artifacts and caches"
	@echo "  make pre-commit    - Run pre-commit hooks on all files"
	@echo "  make security      - Run security scans (bandit, safety)"
	@echo ""

# Install base package
install:
	pip install -e ".[full]"

# Install development environment
dev-install: install
	pip install -r contrib/requirements/requirements-dev.txt
	pre-commit install
	@echo "✅ Development environment ready!"
	@echo "Pre-commit hooks installed. They will run automatically on git commit."

# Run tests
test:
	python -m pytest electrum/tests/ -v

# Run test with coverage
test-cov:
	python -m pytest electrum/tests/ --cov=electrum --cov-report=term-missing

# Format code
format:
	black electrum/ --line-length=100
	isort electrum/ --profile black --line-length 100

# Check formatting without modifying
format-check:
	black electrum/ --line-length=100 --check
	isort electrum/ --profile black --line-length 100 --check

# Run linters
lint:
	ruff check electrum/
	flake8 electrum/ --count --select=E9,E101,E129,E273,E274,E703,E71,E722,F63,F7,F82,W191,W29,B --ignore=B007,B009,B010,B019 --show-source --statistics --exclude="*_pb2.py,electrum/_vendor/"

# Type checking
type-check:
	mypy --ignore-missing-imports --python-version=3.12 electrum --exclude="electrum/tests|electrum/gui/qt/forms|electrum/locale"

# Security scanning
security:
	@echo "🔒 Running security scans..."
	bandit -r electrum/ -ll --skip B101,B601,B603 -f json -o bandit-report.json || true
	@echo "Bandit scan complete (report: bandit-report.json)"
	safety check --policy-file .safety-policy.json --json || true
	@echo "Safety dependency scan complete"

# Security scan with detailed output
security-verbose:
	bandit -r electrum/ -ll --skip B101,B601,B603
	safety check --policy-file .safety-policy.json

# Run pre-commit on all files
pre-commit:
	pre-commit run --all-files

# Clean build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ 2>/dev/null || true
	@echo "✅ Cleaned build artifacts and caches"

# Quick check before committing
check: format-check lint type-check
	@echo "✅ All checks passed!"

# Development server
run:
	./run_electrum --testnet

# Build distribution
build:
	python setup.py sdist bdist_wheel

# Generate documentation
docs:
	sphinx-build -b html docs/ docs/_build/html
	@echo "📚 Documentation built at docs/_build/html/index.html"