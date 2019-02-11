#!/bin/bash

# This script builds a release for BlenderSync
if [ "$#" -ne 1 ]; then
    echo "The correct usage of this script is './release_gen.sh release-type'\n"
    echo "Where release-type can be either 'dev' or 'prod'."
    echo "'dev' will build using the latest master branch from git."
    echo "'prod' will build using pip to pull dependencies."
    exit 64
fi
RELEASE_TYPE=$1
RELEASE_OPT="prod"

if [ $RELEASE_TYPE != "prod" ]; then
  RELEASE_OPT="dev"
fi


printf "Generating BlenderSync Release of type $RELEASE_OPT\n"

# Tear down any existing dependency folders
if [ -d ./animation_client ]; then
  sudo rm -r ./animation_client/
fi

# Build a temp directory to clone stuff into
mkdir tmp

if [ $RELEASE_OPT = "prod" ]; then

  echo "Not implemented\n"

else

  cd tmp && git clone https://github.com/AO-StreetArt/AeselAnimationClient.git && cd ../
  mv tmp/AeselAnimationClient/animation_client/ .
  sudo rm -r animation_client/api_wrapper/

fi

# Tear down our temp directory
sudo rm -r tmp/

# Generate our final zip file
cd ../ && zip -r BlenderSync.zip BlenderSync/ -x *.git* -x *.blend
