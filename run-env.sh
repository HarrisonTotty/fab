#!/usr/bin/env bash
# Runs an instance of the fab Jupyter Lab environment image.

set -e

docker run \
    --rm \
    -p 8888:8888 \
    -v "${PWD}/data:/home/jovyan/work/data" \
    -v "${PWD}/notebooks:/home/jovyan/work/notebooks" \
    fab:latest start.sh jupyter lab --LabApp.token=''
