#!/usr/bin/env bash
# Builds the fab Jupyter Lab environment image.

set -e
trap 'exit 100' INT

if [ ! -f Dockerfile ]; then
    echo 'Please execute this script within the too directory of the fab repository.'
    exit 1
fi

docker build -t fab:latest .
