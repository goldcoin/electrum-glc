#!/bin/bash
#
# env vars:
# - ELECBUILD_NOCACHE: if set, forces rebuild of docker image
# - ELECBUILD_COMMIT: if set, do a fresh clone and git checkout

set -e

PROJECT_ROOT="$(dirname "$(readlink -e "$0")")/../../.."
PROJECT_ROOT_OR_FRESHCLONE_ROOT="$PROJECT_ROOT"
CONTRIB="$PROJECT_ROOT/contrib"
CONTRIB_APPIMAGE="$CONTRIB/build-linux/appimage"
DISTDIR="$PROJECT_ROOT/dist"
BUILD_UID=$(/usr/bin/stat -c %u "$PROJECT_ROOT")

. "$CONTRIB"/build_tools_util.sh


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
    -t electrum-glc-appimage-builder-shasta \
    "$CONTRIB_APPIMAGE"

# maybe do fresh clone
if [ ! -z "$ELECBUILD_COMMIT" ] ; then
    info "ELECBUILD_COMMIT=$ELECBUILD_COMMIT. doing fresh clone and git checkout."
    FRESH_CLONE="/tmp/electrum_build/appimage/fresh_clone/electrum"
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
    --name electrum-glc-appimage-builder-cont-shasta \
    -v "$PROJECT_ROOT_OR_FRESHCLONE_ROOT":/opt/electrum \
    -e MAKEFLAGS="-j8" \
    --rm \
    --workdir /opt/electrum/contrib/build-linux/appimage \
    electrum-glc-appimage-builder-shasta \
    ./make_appimage.sh

# make sure resulting binary location is independent of fresh_clone
if [ ! -z "$ELECBUILD_COMMIT" ] ; then
    mkdir --parents "$DISTDIR/"
    cp -f "$FRESH_CLONE/dist"/* "$DISTDIR/"
fi
