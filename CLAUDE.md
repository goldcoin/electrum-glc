# Claude AI Assistant Guide for Goldcoin Electrum

## Overview

This document provides guidance for Claude AI (or other AI assistants) when working with the Goldcoin Electrum codebase. It contains essential context, common tasks, and project-specific knowledge to ensure efficient and accurate assistance.

## Project Context

**Goldcoin Electrum** is a lightweight cryptocurrency wallet for Goldcoin (GLC), forked from the original Electrum Bitcoin wallet. The codebase is actively maintained and follows modern Python development practices.

### Key Technologies
- **Language:** Python 3.12+
- **GUI Framework:** PyQt5 (migrating to PyQt6)
- **Async Framework:** asyncio with aiorpcx
- **Testing:** pytest
- **CI/CD:** Cirrus CI
- **Platforms:** Windows, macOS, Linux, Android

## Repository Structure

```
electrum-glc/
├── electrum/              # Main application code
│   ├── gui/              # GUI implementations (Qt, QML, text)
│   ├── plugins/          # Hardware wallet & feature plugins
│   ├── tests/            # Test suite
│   └── *.py              # Core modules
├── contrib/              # Build scripts and requirements
│   ├── requirements/     # Dependency specifications
│   ├── build-wine/       # Windows build
│   ├── osx/             # macOS build
│   └── android/         # Android build
├── run_electrum          # Main entry point script
└── setup.py             # Package configuration
```

## Common Development Tasks

### Quick Start (NEW - Phase 1 Complete!)
```bash
# Set up complete development environment
make dev-install

# Run all quality checks before committing
make check

# Format code automatically
make format

# Run tests with coverage
make test-cov
```

### 1. Running Tests
```bash
# Using Makefile (recommended)
make test                    # Run all tests
make test-cov               # Run with coverage report

# Manual commands
python -m pytest electrum/tests/
python -m pytest electrum/tests/test_bitcoin.py
python -m pytest --cov=electrum electrum/tests/
```

### 2. Code Quality Checks
```bash
# Using Makefile (recommended)
make lint                   # Run all linters
make format                 # Auto-format code
make format-check          # Check formatting without changes
make type-check            # Run mypy type checking
make security              # Run security scans
make pre-commit            # Run all pre-commit hooks

# Manual commands
ruff check electrum/
mypy electrum/
black electrum/ --line-length=100
isort electrum/ --profile black
bandit -r electrum/
```

### 3. Building the Application
```bash
# Using Makefile
make install               # Install Electrum with dependencies
make build                 # Create distribution packages

# Manual commands
pip install -e ".[full]"
python setup.py sdist bdist_wheel
```

## Important Files to Know

- **electrum/version.py** - Version information
- **electrum/bitcoin.py** - Core Bitcoin/Goldcoin operations
- **electrum/blockchain.py** - Blockchain verification (contains scrypt usage)
- **electrum/network.py** - Network communication
- **electrum/wallet.py** - Wallet management
- **electrum/gui/qt/main_window.py** - Main Qt window

## Current Modernization Status

### Phase 1: COMPLETED ✅ (August 2025)
- ✅ Python 3.12 upgrade across all files
- ✅ Scrypt dependency updated to 0.9.4
- ✅ Created pyproject.toml with full tool configurations
- ✅ Modernization roadmap documented (MODERNIZATION.md)
- ✅ Pre-commit hooks configured (.pre-commit-config.yaml)
- ✅ Code formatters configured (black, isort, ruff)
- ✅ Type checking added to CI (mypy)
- ✅ Development Makefile created
- ✅ Requirements-dev.txt for development tools
- ✅ Python version consistency fixed (3.12 minimum everywhere)

### Phase 2: COMPLETED ✅ (August 2025)
- ✅ PyQt6 compatibility layer (electrum/gui/qt/qt_compat.py)
- ✅ Security scanning tools (bandit, safety configured)
- ✅ GitHub Actions workflow (.github/workflows/ci.yml)
- ✅ Dependabot configuration (.github/dependabot.yml)

### Phase 3: PENDING (Weeks 5-8)
- ⏳ Complete PyQt6 migration
- ⏳ Documentation generation with Sphinx
- ⏳ Enhanced testing infrastructure

## Code Style Guidelines

### Python Code
- **Line length:** 100 characters (will be enforced by black)
- **Type hints:** Required for all new functions
- **Docstrings:** Google style for public APIs
- **Async:** Prefer async/await over threading for I/O
- **Imports:** Absolute imports preferred

### Git Commits
- **Format:** `<type>: <description>`
- **Types:** feat, fix, docs, style, refactor, test, chore
- **Example:** `feat: add hardware wallet support for Model X`

## Testing Guidelines

### Test Structure
- Unit tests in `electrum/tests/test_*.py`
- Functional tests in `electrum/tests/test_regtest.py`
- GUI tests in `electrum/tests/test_gui_qt.py`

### Test Requirements
- All new features must have tests
- Maintain >80% code coverage
- Tests must pass on all platforms

## Security Considerations

### Critical Areas
- **Private key handling** - Never log or expose
- **Seed phrase management** - Always encrypted in memory
- **Network communication** - Verify SSL certificates
- **Hardware wallet integration** - Follow vendor security guidelines

### Dependency Management
- Review all dependency updates for security implications
- Use pinned versions in production builds
- Run safety checks regularly

## Hardware Wallet Support

### Supported Devices
- Ledger (Nano S/X)
- Trezor (One/T)
- KeepKey
- Coldcard
- BitBox02

### Plugin Architecture
- Each hardware wallet has a plugin in `electrum/plugins/`
- Plugins are loaded dynamically based on device detection
- Follow existing plugin patterns when adding new devices

## Build System Notes

### Platform-Specific Builds
- **Windows:** Uses Wine for cross-compilation
- **macOS:** Requires code signing for distribution
- **Android:** Built with python-for-android
- **Linux:** AppImage for distribution

### Deterministic Builds
- All release builds must be reproducible
- Use contrib/deterministic-build/ scripts
- Verify builds match published hashes

## Common Issues and Solutions

### Issue: Scrypt import fails
**Solution:** Install scrypt wheels or fall back to pure Python implementation

### Issue: Qt GUI not starting
**Solution:** Check PyQt5 installation and Qt platform plugins

### Issue: Hardware wallet not detected
**Solution:** Install udev rules (Linux) or check USB permissions

## Performance Considerations

- **Blockchain verification** is CPU-intensive (scrypt hashing)
- **Network synchronization** can be bandwidth-heavy
- **GUI responsiveness** - Keep heavy operations in background threads
- **Memory usage** - Watch for leaks in long-running operations

## Future Roadmap Awareness

When making changes, consider:
1. **PyQt6 migration** - Avoid PyQt5-specific patterns
2. **Python 3.12+ features** - Use modern syntax where appropriate
3. **Type safety** - Add type hints to all modifications
4. **Async patterns** - Prefer async over threading

## Useful Commands for Development

```bash
# Quick development workflow (NEW!)
make dev-install           # One-time setup
make format                # Format your code
make check                 # Run all checks
git commit                 # Pre-commit hooks run automatically

# Run Electrum in testnet mode
./run_electrum --testnet
# or
make run

# Run with debug logging
./run_electrum -v

# Run offline
./run_electrum --offline

# Run with specific wallet file
./run_electrum -w /path/to/wallet

# Generate console command
./run_electrum daemon -d
./run_electrum daemon load_wallet

# Clean up development artifacts
make clean
```

## New Development Files (Phase 1)

### Configuration Files Added
- **`.pre-commit-config.yaml`** - Pre-commit hooks configuration
- **`pyproject.toml`** - Modern Python project configuration with tool settings
- **`Makefile`** - Development automation commands
- **`contrib/requirements/requirements-dev.txt`** - Development dependencies

### Documentation Added
- **`MODERNIZATION.md`** - Complete modernization roadmap
- **`CLAUDE.md`** - This file, AI assistant guide

## Contact and Resources

- **Repository:** github.com/goldcoin/electrum-glc
- **Issues:** Report bugs via GitHub Issues
- **Documentation:** See /docs directory
- **Community:** Goldcoin Discord/Forum

## Notes for AI Assistants

1. **Always check existing patterns** before implementing new features
2. **Prioritize security** in all code modifications
3. **Maintain backward compatibility** unless explicitly told otherwise
4. **Test on multiple platforms** when possible
5. **Follow the modernization roadmap** in MODERNIZATION.md
6. **Use type hints** in all new code
7. **Write tests** for all new functionality
8. **Document significant changes** in code comments

## Summary of Phase 1 Changes

### What Changed
1. **Python version:** Now requires Python 3.12+ everywhere
2. **Development tools:** Complete suite of formatters, linters, and type checkers
3. **Pre-commit hooks:** Automatic code quality checks on every commit
4. **CI/CD:** Added mypy type checking, updated Python test versions
5. **Developer experience:** Simple Makefile commands for all common tasks

### How to Work with the Modernized Codebase
1. Always run `make dev-install` after cloning
2. Use `make format` before committing code
3. Run `make check` to ensure code quality
4. Pre-commit hooks will catch issues automatically
5. Follow the type hints and add them to new code
6. Check `MODERNIZATION.md` for upcoming changes

### Next Session Tasks (Phase 3)
When continuing development, focus on:
- Complete PyQt6 migration throughout codebase
- Set up Sphinx documentation generation
- Enhance testing infrastructure
- Performance optimization

---

*Last Updated: August 2025*  
*Version: 3.0* - Phase 2 Complete
*Author: Goldcoin Development Team with Claude AI Assistant*