#!/bin/sh
# Build linux/amd64 and linux/arm64 images. Context is the catalog repository root.
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
IMAGE="${IMAGE:-ecosystemai/ecosystem-domain-catalog}"
TAG="${TAG:-latest}"

case "$(uname -m)" in
  arm64 | aarch64) NATIVE=arm64 ;;
  *) NATIVE=amd64 ;;
esac

for ARCH in amd64 arm64; do
  docker build \
    --platform "linux/${ARCH}" \
    -f "${SCRIPT_DIR}/Dockerfile" \
    -t "${IMAGE}:${ARCH}" \
    "${REPO_ROOT}"
done

docker tag "${IMAGE}:${NATIVE}" "${IMAGE}:${TAG}"
docker tag "${IMAGE}:${NATIVE}" ecosystem-domain-catalog:local

echo "Built ${IMAGE}:amd64 and ${IMAGE}:arm64"
echo "Tagged native (${NATIVE}) as ${IMAGE}:${TAG} and ecosystem-domain-catalog:local"
