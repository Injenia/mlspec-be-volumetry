#!/usr/bin/env bash
set -e
set -x

VERSION=${1:-'0.0.1'}
GCP_PROJECT=${2:-$GCP_PROJECT}

NAME=be_volumetry

docker tag $NAME gcr.io/$GCP_PROJECT/$NAME:$VERSION
docker push gcr.io/$GCP_PROJECT/$NAME:$VERSION
