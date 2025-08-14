# Electrum-GLC Enterprise Deterministic Build System Design

## Overview

This document outlines the architecture for a world-class deterministic build system for Electrum-GLC, designed to be maintained by AI systems for years to come.

## Core Principles

1. **Complete Reproducibility**: Byte-for-byte identical outputs given the same inputs
2. **Supply Chain Security**: Cryptographic verification at every step
3. **Build Isolation**: No external dependencies during build time
4. **Temporal Independence**: Builds produce identical results regardless of when they're run
5. **Platform Agnostic**: Same build process works on any host system
6. **AI Maintainable**: Clear, documented, and self-verifying

## Architecture Components

### 1. Package Mirror System

**Purpose**: Ensure all dependencies are available and immutable

**Implementation**:
- Local package repository with all required packages
- SHA256 verification for every package
- Git LFS or dedicated artifact storage for binary packages
- Fallback to multiple mirrors with verification

**Structure**:
```
contrib/deterministic-build/packages/
├── manifest.json           # Package index with hashes
├── python/
│   ├── wheels/            # Binary wheels with exact versions
│   └── source/            # Source distributions
├── wine/
│   └── installers/        # Wine and Python installers
└── verification/
    └── signatures/        # GPG signatures for packages
```

### 2. Multi-Stage Docker Build

**Stage 1: Base System**
- Immutable base image with fixed SHA256
- All system packages pinned to specific versions
- Debian snapshot repositories for reproducibility

**Stage 2: Build Tools**
- Wine installation from cached packages
- Python installation from verified MSI files
- Compiler toolchain setup

**Stage 3: Package Installation**
- Install from local package mirror
- No network access during this stage
- Cryptographic verification of all packages

**Stage 4: Application Build**
- Build Electrum with PyInstaller
- Generate NSIS installer
- Apply deterministic timestamps

**Stage 5: Verification**
- Verify checksums
- Run basic smoke tests
- Generate build attestation

### 3. Build Attestation System

**Components**:
- Build manifest with all input hashes
- Reproducible build proof
- Signed attestation document
- Build environment snapshot

**Format**:
```json
{
  "version": "1.0",
  "timestamp": "2025-08-14T00:00:00Z",
  "source_commit": "sha256:...",
  "docker_image": "sha256:...",
  "packages": {
    "package_name": {
      "version": "x.y.z",
      "hash": "sha256:..."
    }
  },
  "output": {
    "electrum-glc-4.5.0-setup.exe": {
      "hash": "sha256:...",
      "size": 12345678
    }
  },
  "build_environment": {
    "SOURCE_DATE_EPOCH": 1000000000,
    "PYTHONHASHSEED": "0"
  }
}
```

### 4. Package Management Strategy

**Three-Tier System**:

1. **Tier 1: Core Dependencies**
   - pip, setuptools, wheel
   - Must be binary wheels for bootstrap
   - Stored in git repository

2. **Tier 2: Build Dependencies**
   - PyInstaller, NSIS tools
   - Can be built from source
   - Cached after first build

3. **Tier 3: Application Dependencies**
   - Electrum requirements
   - Built from source for security
   - Exceptions for binary-only packages (scrypt)

### 5. Deterministic Environment Variables

```bash
# Temporal determinism
export SOURCE_DATE_EPOCH=1000000000
export PYTHONHASHSEED=0
export PYTHONDONTWRITEBYTECODE=1
export TZ=UTC

# Build determinism
export DETERMINISTIC_BUILD=1
export NO_NETWORK=1
export MAKEFLAGS="-j1"  # Serial builds for reproducibility

# Wine determinism
export WINEDEBUG=-all
export WINEARCH=win64
export WINEPREFIX=/opt/wine64
```

### 6. Build Verification Pipeline

**Step 1: Pre-build Verification**
- Verify all package hashes
- Check Docker image integrity
- Validate build environment

**Step 2: Build Execution**
- Execute build in isolated environment
- Log all operations
- Generate build manifest

**Step 3: Post-build Verification**
- Compare output hashes with expected
- Run multiple builds and compare
- Generate signed attestation

### 7. CI/CD Integration

**GitHub Actions Workflow**:
```yaml
name: Deterministic Build
on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Setup deterministic environment
      - name: Load package mirror
      - name: Build in Docker
      - name: Verify reproducibility
      - name: Sign and attest
      - name: Upload artifacts
```

## Implementation Plan

### Phase 1: Package Mirror Infrastructure (Week 1)
- Set up local package repository
- Download and verify all dependencies
- Create package manifest system
- Implement verification scripts

### Phase 2: Docker Build Refactor (Week 2)
- Implement multi-stage Dockerfile
- Add build caching layers
- Integrate package mirror
- Remove network dependencies

### Phase 3: Determinism Improvements (Week 3)
- Implement SOURCE_DATE_EPOCH throughout
- Fix all timestamp issues
- Ensure serial builds where needed
- Add environment validation

### Phase 4: Verification & Attestation (Week 4)
- Build verification scripts
- Attestation generation
- Multiple build comparison
- Documentation and testing

## Security Considerations

1. **Supply Chain Attacks**: All packages verified with SHA256
2. **Build Environment Tampering**: Docker image verified
3. **Time-based Attacks**: SOURCE_DATE_EPOCH prevents
4. **Network MITM**: No network access during build
5. **Compiler Backdoors**: Reproducible builds detect

## Maintenance Guidelines for AI Systems

1. **Package Updates**: 
   - Always verify new package hashes
   - Test reproducibility before committing
   - Update manifest.json atomically

2. **Build Failures**:
   - Check package mirror integrity first
   - Verify Docker base image hasn't changed
   - Ensure all environment variables set

3. **Verification Failures**:
   - Compare build logs for differences
   - Check for non-deterministic operations
   - Verify SOURCE_DATE_EPOCH is respected

## Success Criteria

- [ ] Identical builds on different machines
- [ ] Identical builds at different times
- [ ] No network access during build
- [ ] All packages cryptographically verified
- [ ] Build attestation generated and signed
- [ ] Documentation complete and clear
- [ ] AI can maintain without human intervention

## Conclusion

This enterprise-grade deterministic build system ensures that Electrum-GLC can be built reproducibly, securely, and reliably for years to come, even under full AI maintenance. The system prioritizes security, reproducibility, and maintainability over speed or convenience.