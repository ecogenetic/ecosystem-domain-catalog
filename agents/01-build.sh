#!/usr/bin/env bash
# Build linux/amd64 and linux/arm64 images. Context is the catalog repository root.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
IMAGE="${IMAGE:-ecosystemai/ecosystem-domain-catalog}"
TAG="${TAG:-latest}"

case "$(uname -m)" in
  arm64 | aarch64) NATIVE=arm64 ;;
  *) NATIVE=amd64 ;;
esac

if ! docker buildx inspect ecosystem-domain-catalog >/dev/null 2>&1; then
  docker buildx create --name ecosystem-domain-catalog --driver docker-container --bootstrap
fi
docker buildx use ecosystem-domain-catalog

for ARCH in amd64 arm64; do
  docker buildx build \
    --platform "linux/${ARCH}" \
    --load \
    -f "${SCRIPT_DIR}/Dockerfile" \
    -t "${IMAGE}:${ARCH}" \
    "${REPO_ROOT}"
done

docker tag "${IMAGE}:${NATIVE}" "${IMAGE}:${TAG}"
docker tag "${IMAGE}:${NATIVE}" ecosystem-domain-catalog:local

echo "Built ${IMAGE}:amd64 and ${IMAGE}:arm64"
echo "Tagged native (${NATIVE}) as ${IMAGE}:${TAG} and ecosystem-domain-catalog:local"
