#!/usr/bin/env bash
set -e
set -x

if [ ! -f Dockerfile ]; then
    echo "Dockerfile not found. You should launch this script from the root"
    exit 1
fi

docker build -t be_volumetry .
