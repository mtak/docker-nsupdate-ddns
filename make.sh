#!/bin/bash

VERSION="1.0"
NAMESPACE='merijntjetak'
IMAGENAME='docker-nsupdate-ddns'
DOCKER_REGISTRY_HOST=''
DOCKER_REGISTRY_PORT=''

# Generate docker URI
if [[ "x$DOCKER_REGISTRY_HOST" != "x" && "x$DOCKER_REGISTRY_PORT" != "x" ]]; then
  DOCKER_REGISTRY_AUTHORITY="${DOCKER_REGISTRY_HOST}:${DOCKER_REGISTRY_PORT}/"
else
  DOCKER_REGISTRY_AUTHORITY=''
fi

if [[ "$1" == "build" ]]; then
  docker build -t ${NAMESPACE}/${IMAGENAME} -t ${NAMESPACE}/${IMAGENAME}:${VERSION} .

elif [[ "$1" == "run" ]]; then
  docker run -ti --rm \
    -v '/var/run/docker.sock:/var/run/docker.sock' \
    -v `pwd`/config:/config \
    ${NAMESPACE}/${IMAGENAME}:${VERSION} \
    /config

elif [[ "$1" == "publish" ]]; then
  docker tag ${PUBLISHER}/${IMAGENAME}:${VERSION} ${DOCKER_REGISTRY_AUTHORITY}${NAMESPACE}/${IMAGENAME}:$VERSION
  docker push ${DOCKER_REGISTRY_AUTHORITY}${NAMESPACE}/${IMAGENAME}:$VERSION

else
  cat <<EOF
Usage: $0 action

Actions:
  build   - Build docker image
  run     - Run docker image
  publish - Publish docker image

Change the parameters in the run section to adjust for local testing variables.
EOF

fi
