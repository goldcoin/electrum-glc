#!/bin/bash
#
# env vars:
# - ELECBUILD_NOCACHE: if set, forces rebuild of docker image
# - ELECBUILD_COMMIT: if set, do a fresh clone and git checkout

set -e

# Set non-interactive mode if no TTY is available (e.g., in CI)
if [ ! -t 0 ]; then
    export DEBIAN_FRONTEND=noninteractive
    export DOCKER_BUILDKIT=1
fi

PROJECT_ROOT="$(dirname "$(readlink -e "$0")")/../.."
PROJECT_ROOT_OR_FRESHCLONE_ROOT="$PROJECT_ROOT"
CONTRIB="$PROJECT_ROOT/contrib"
CONTRIB_WINE="$CONTRIB/build-wine"
BUILD_UID=$(/usr/bin/stat -c %u "$PROJECT_ROOT")

. "$CONTRIB"/build_tools_util.sh

info "Clearing $CONTRIB_WINE/dist..."
rm -rf "$CONTRIB_WINE"/dist/*


DOCKER_BUILD_FLAGS=""
if [ ! -z "$ELECBUILD_NOCACHE" ] ; then
    info "ELECBUILD_NOCACHE is set. forcing rebuild of docker image."
    DOCKER_BUILD_FLAGS="--pull --no-cache"
fi

if [ -z "$ELECBUILD_COMMIT" ] ; then  # local dev build
    DOCKER_BUILD_FLAGS="$DOCKER_BUILD_FLAGS --build-arg UID=$BUILD_UID"
fi

info "building docker image."
docker build \
    $DOCKER_BUILD_FLAGS \
    -t electrum-glc-wine-builder-shasta \
    "$CONTRIB_WINE"

# maybe do fresh clone
if [ ! -z "$ELECBUILD_COMMIT" ] ; then
    info "ELECBUILD_COMMIT=$ELECBUILD_COMMIT. doing fresh clone and git checkout."
    FRESH_CLONE="/tmp/electrum_build/windows/fresh_clone/electrum"
    rm -rf "$FRESH_CLONE" 2>/dev/null || ( info "we need sudo to rm prev FRESH_CLONE." && sudo rm -rf "$FRESH_CLONE" )
    umask 0022
    git clone "$PROJECT_ROOT" "$FRESH_CLONE"
    cd "$FRESH_CLONE"
    git checkout "$ELECBUILD_COMMIT"
    PROJECT_ROOT_OR_FRESHCLONE_ROOT="$FRESH_CLONE"
else
    info "not doing fresh clone."
fi

info "building binary..."
# check uid and maybe chown. see #8261
if [ ! -z "$ELECBUILD_COMMIT" ] ; then  # fresh clone (reproducible build)
    if [ $(id -u) != "1000" ] || [ $(id -g) != "1000" ] ; then
        info "Fresh clone will be accessed with Docker's default user (uid 1000)"
        # Docker container runs as user:1000 - will handle file ownership internally
    fi
fi

# Check if we're in a CI environment or if TTY is not available
DOCKER_RUN_FLAGS="-i"
if [ -t 0 ] ; then
    # TTY is available, use interactive mode
    DOCKER_RUN_FLAGS="-it"
fi

docker run $DOCKER_RUN_FLAGS \
    --name electrum-glc-wine-builder-cont-shasta \
    -v "$PROJECT_ROOT_OR_FRESHCLONE_ROOT":/opt/wine64/drive_c/electrum \
    -e MAKEFLAGS="-j8" \
    --rm \
    --workdir /opt/wine64/drive_c/electrum/contrib/build-wine \
    electrum-glc-wine-builder-shasta \
    ./make_win.sh

# make sure resulting binary location is independent of fresh_clone
if [ ! -z "$ELECBUILD_COMMIT" ] ; then
    mkdir --parents "$PROJECT_ROOT/contrib/build-wine/dist/"
    cp -f "$FRESH_CLONE/contrib/build-wine/dist"/*.exe "$PROJECT_ROOT/contrib/build-wine/dist/"
fi
