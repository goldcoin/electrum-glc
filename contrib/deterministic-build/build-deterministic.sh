#!/bin/bash
# Enterprise Deterministic Build Orchestrator for Electrum-GLC
# This script manages the complete deterministic build process

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
MIRROR_DIR="${SCRIPT_DIR}/mirror"
OUTPUT_DIR="${SCRIPT_DIR}/output"
ATTESTATION_DIR="${SCRIPT_DIR}/attestations"

# Build configuration
export SOURCE_DATE_EPOCH=1000000000
export PYTHONHASHSEED=0
export PYTHONDONTWRITEBYTECODE=1
export TZ=UTC
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export DETERMINISTIC_BUILD=1

# Docker configuration - use username for uniqueness on shared server
USERNAME=$(whoami)
DOCKER_IMAGE="electrum-glc-deterministic-${USERNAME}:4.5.0"
DOCKER_CONTAINER_PREFIX="electrum-glc-build-${USERNAME}"
DOCKER_BUILDKIT=1

# Functions

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker version &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

setup_directories() {
    log_info "Setting up build directories..."
    
    mkdir -p "${BUILD_DIR}"
    mkdir -p "${OUTPUT_DIR}"
    mkdir -p "${ATTESTATION_DIR}"
    mkdir -p "${MIRROR_DIR}"
    
    log_success "Directories created"
}

create_package_mirror() {
    log_info "Creating package mirror..."
    
    if [ -f "${MIRROR_DIR}/manifest.json" ]; then
        log_info "Package mirror already exists, verifying..."
        python3 "${SCRIPT_DIR}/create_package_mirror.py" --verify-only
    else
        log_info "Building package mirror from scratch..."
        python3 "${SCRIPT_DIR}/create_package_mirror.py"
    fi
    
    log_success "Package mirror ready"
}

prepare_build_context() {
    log_info "Preparing build context..."
    
    # Create build context directory (outside of contrib to avoid recursion)
    BUILD_CONTEXT_DIR="/tmp/electrum-glc-build-${USERNAME}-$$"
    rm -rf "${BUILD_CONTEXT_DIR}"
    mkdir -p "${BUILD_CONTEXT_DIR}"
    
    # Copy necessary files
    cp -r "${PROJECT_ROOT}/electrum" "${BUILD_CONTEXT_DIR}/"
    cp -r "${PROJECT_ROOT}/contrib" "${BUILD_CONTEXT_DIR}/"
    cp "${PROJECT_ROOT}/setup.py" "${BUILD_CONTEXT_DIR}/" 2>/dev/null || true
    cp "${PROJECT_ROOT}/run_electrum" "${BUILD_CONTEXT_DIR}/" 2>/dev/null || true
    
    # Copy mirror
    cp -r "${MIRROR_DIR}" "${BUILD_CONTEXT_DIR}/mirror"
    
    # Set deterministic timestamps
    find "${BUILD_CONTEXT_DIR}" -exec touch -h -d "@${SOURCE_DATE_EPOCH}" {} +
    
    # Store path for Docker build
    echo "${BUILD_CONTEXT_DIR}" > /tmp/build-context-${USERNAME}.path
    
    log_success "Build context prepared"
}

build_docker_image() {
    log_info "Building Docker image..."
    
    # Get the build context directory
    BUILD_CONTEXT_DIR=$(cat /tmp/build-context-${USERNAME}.path)
    cd "${BUILD_CONTEXT_DIR}"
    
    # Build with BuildKit for better caching
    # Copy the Dockerfile to build context
    cp "${PROJECT_ROOT}/contrib/build-wine/Dockerfile" "${BUILD_CONTEXT_DIR}/"
    cp "${PROJECT_ROOT}/contrib/build-wine/apt.sources.list" "${BUILD_CONTEXT_DIR}/"
    cp "${PROJECT_ROOT}/contrib/build-wine/apt.preferences" "${BUILD_CONTEXT_DIR}/"
    
    DOCKER_BUILDKIT=1 docker build \
        --build-arg UID="$(id -u)" \
        -f "${BUILD_CONTEXT_DIR}/Dockerfile" \
        -t "${DOCKER_IMAGE}" \
        .
    
    log_success "Docker image built"
}

run_build() {
    log_info "Running deterministic build..."
    
    # Run build in Docker with unique container name
    CONTAINER_NAME="${DOCKER_CONTAINER_PREFIX}-$(date +%s)-$$"
    docker run \
        --name "${CONTAINER_NAME}" \
        --rm \
        -v "${OUTPUT_DIR}:/output" \
        -e SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}" \
        -e PYTHONHASHSEED="${PYTHONHASHSEED}" \
        -e PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE}" \
        -e TZ="${TZ}" \
        -e LC_ALL="${LC_ALL}" \
        -e LANG="${LANG}" \
        -e DETERMINISTIC_BUILD="${DETERMINISTIC_BUILD}" \
        "${DOCKER_IMAGE}" \
        /bin/bash -c "cp /opt/electrum-glc/dist/*.exe /output/" 2>/dev/null || true
    
    log_success "Build completed"
}

verify_build() {
    log_info "Verifying build outputs..."
    
    # Generate hashes for this build
    python3 "${SCRIPT_DIR}/verify-build.py" generate \
        --directory "${OUTPUT_DIR}" \
        --output "${BUILD_DIR}/build-hashes.json"
    
    # If we have expected hashes, verify against them
    if [ -f "${SCRIPT_DIR}/expected-hashes.json" ]; then
        python3 "${SCRIPT_DIR}/verify-build.py" verify \
            --expected "${SCRIPT_DIR}/expected-hashes.json" \
            --actual "${OUTPUT_DIR}"
    else
        log_warning "No expected hashes found, skipping verification"
    fi
    
    log_success "Build verification complete"
}

generate_attestation() {
    log_info "Generating build attestation..."
    
    # Get Docker image ID
    DOCKER_IMAGE_ID=$(docker images -q "${DOCKER_IMAGE}")
    
    # Generate attestation
    python3 "${SCRIPT_DIR}/generate-attestation.py" generate \
        --source "${PROJECT_ROOT}" \
        --output-dir "${OUTPUT_DIR}" \
        --docker-image "${DOCKER_IMAGE}:${DOCKER_IMAGE_ID}" \
        --manifest "${MIRROR_DIR}/manifest.json" \
        --output "${ATTESTATION_DIR}/build-attestation-$(date +%Y%m%d-%H%M%S).json"
    
    log_success "Build attestation generated"
}

run_reproducibility_test() {
    log_info "Running reproducibility test..."
    
    # Create second build directory
    OUTPUT_DIR2="${SCRIPT_DIR}/output2"
    mkdir -p "${OUTPUT_DIR2}"
    
    # Run second build
    log_info "Running second build for comparison..."
    docker run \
        --rm \
        -v "${OUTPUT_DIR2}:/output" \
        -e SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}" \
        -e PYTHONHASHSEED="${PYTHONHASHSEED}" \
        -e PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE}" \
        -e TZ="${TZ}" \
        -e LC_ALL="${LC_ALL}" \
        -e LANG="${LANG}" \
        -e DETERMINISTIC_BUILD="${DETERMINISTIC_BUILD}" \
        "${DOCKER_IMAGE}" \
        /bin/bash -c "cp /opt/electrum-glc/dist/*.exe /output/"
    
    # Compare builds
    python3 "${SCRIPT_DIR}/verify-build.py" compare \
        --build1 "${OUTPUT_DIR}" \
        --build2 "${OUTPUT_DIR2}"
    
    RESULT=$?
    
    # Clean up second build
    rm -rf "${OUTPUT_DIR2}"
    
    if [ $RESULT -eq 0 ]; then
        log_success "Reproducibility test PASSED - builds are identical!"
    else
        log_error "Reproducibility test FAILED - builds differ!"
        exit 1
    fi
}

clean_build() {
    log_info "Cleaning build artifacts..."
    
    rm -rf "${BUILD_DIR}"
    rm -rf "${OUTPUT_DIR}"
    
    # Clean up temporary build contexts
    rm -rf /tmp/electrum-glc-build-${USERNAME}-*
    rm -f /tmp/build-context-${USERNAME}.path
    
    # Remove Docker images if requested
    if [ "${1:-}" = "--docker" ]; then
        log_info "Removing Docker images..."
        docker rmi "${DOCKER_IMAGE}" 2>/dev/null || true
    fi
    
    log_success "Build cleaned"
}

# Main execution
main() {
    echo "=================================================="
    echo "  Electrum-GLC Enterprise Deterministic Build"
    echo "  Version: 4.5.0"
    echo "  Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    echo "=================================================="
    echo ""
    
    # Parse arguments
    COMMAND="${1:-build}"
    
    case "$COMMAND" in
        build)
            check_prerequisites
            setup_directories
            create_package_mirror
            prepare_build_context
            build_docker_image
            run_build
            verify_build
            generate_attestation
            ;;
        
        test)
            check_prerequisites
            setup_directories
            
            if [ ! -f "${OUTPUT_DIR}/electrum-glc-4.5.0-setup.exe" ]; then
                log_error "No build found to test. Run 'build' first."
                exit 1
            fi
            
            run_reproducibility_test
            ;;
        
        verify)
            if [ ! -f "${OUTPUT_DIR}/electrum-glc-4.5.0-setup.exe" ]; then
                log_error "No build found to verify."
                exit 1
            fi
            
            verify_build
            ;;
        
        clean)
            clean_build
            ;;
        
        mirror)
            create_package_mirror
            ;;
        
        *)
            echo "Usage: $0 {build|test|verify|clean|mirror}"
            echo ""
            echo "Commands:"
            echo "  build   - Run complete deterministic build"
            echo "  test    - Test build reproducibility"
            echo "  verify  - Verify existing build"
            echo "  clean   - Clean all build artifacts"
            echo "  mirror  - Create/update package mirror"
            exit 1
            ;;
    esac
    
    echo ""
    echo "=================================================="
    echo "  Build completed successfully!"
    echo "  Outputs: ${OUTPUT_DIR}"
    echo "  Attestation: ${ATTESTATION_DIR}"
    echo "=================================================="
}

# Run main function
main "$@"