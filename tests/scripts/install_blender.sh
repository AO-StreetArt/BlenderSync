#!/bin/sh
set -e

HOME=$1

VERSION=2.79
NAME="blender-2.79b-linux-glibc219-x86_64"
CACHE="${HOME}/.blender-cache"
TAR="${CACHE}/${NAME}.tar.bz2"
URL="http://download.blender.org/release/Blender2.79/blender-2.79b-linux-glibc219-x86_64.tar.bz2"

echo "Installing Blender ${VERSION}"
mkdir -p $CACHE
if [ ! -f $TAR ]; then
    wget -O $TAR $URL
fi
tar -xjf $TAR -C $HOME
export BLENDER_FOLDER=$HOME/$NAME
export BLENDER_EXEC=$BLENDER_FOLDER/blender
