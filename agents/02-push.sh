#!/usr/bin/env bash
# Push amd64 and arm64 images to Docker Hub and publish a multi-arch tag.
set -euo pipefail

IMAGE="${IMAGE:-ecosystemai/ecosystem-domain-catalog}"
TAG="${TAG:-latest}"

docker push "${IMAGE}:amd64"
docker push "${IMAGE}:arm64"

docker buildx imagetools create \
  --tag "${IMAGE}:${TAG}" \
  "${IMAGE}:amd64" \
  "${IMAGE}:arm64"

echo "Pushed ${IMAGE}:amd64, ${IMAGE}:arm64, and multi-arch ${IMAGE}:${TAG}"
