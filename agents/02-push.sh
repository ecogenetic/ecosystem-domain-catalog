#!/bin/sh
# Push amd64 and arm64 images to Docker Hub and publish a multi-arch tag.
set -eu

IMAGE="${IMAGE:-ecosystemai/ecosystem-domain-catalog}"
TAG="${TAG:-latest}"

docker push "${IMAGE}:amd64"
docker push "${IMAGE}:arm64"

if ! docker buildx imagetools create \
  --tag "${IMAGE}:${TAG}" \
  "${IMAGE}:amd64" \
  "${IMAGE}:arm64"; then
  docker push "${IMAGE}:${TAG}"
fi

echo "Pushed ${IMAGE}:amd64, ${IMAGE}:arm64, and ${IMAGE}:${TAG}"
