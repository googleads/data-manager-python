#!/bin/bash
set -euo pipefail
set -x # Echo commands for build transparency in Kokoro logs

# -----------------------------------------------------------------------------
# 1. Workspace & Directory Resolution
# -----------------------------------------------------------------------------
# Navigate to the root of the repository
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_DIR}"

echo "=== Building and Releasing from: ${REPO_DIR} ==="

# -----------------------------------------------------------------------------
# 2. Environment & Tooling Setup
# -----------------------------------------------------------------------------
# Upgrade pip and install standard Python build and packaging tools
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade \
    build \
    twine \
    keyrings.google-artifactregistry-auth

# -----------------------------------------------------------------------------
# 3. Clean and Build Distribution Packages
# -----------------------------------------------------------------------------
echo "=== Cleaning previous build artifacts ==="
rm -rf dist/ build/ *.egg-info

echo "=== Building sdist and wheel ==="
python3 -m build

echo "=== Validating built packages with twine ==="
twine --version
twine check dist/*

# -----------------------------------------------------------------------------
# 4. Upload to Internal Exit Gate Artifact Registry
# -----------------------------------------------------------------------------
# keyrings.google-artifactregistry-auth automatically handles authentication
# using the ambient Kokoro BYOSA Service Account.
EXIT_GATE_REPO="https://us-python.pkg.dev/oss-exit-gate-prod/measurement-devrel--pypi"

echo "=== Uploading packages to Exit Gate staging repository: ${EXIT_GATE_REPO} ==="
twine upload --repository-url "${EXIT_GATE_REPO}" dist/*

# -----------------------------------------------------------------------------
# 5. Trigger Exit Gate Release via GCS Manifest
# -----------------------------------------------------------------------------
# If DRY_RUN is set to "true", stop here so you can verify the AR staging
# without publishing to public PyPI.
if [[ "${DRY_RUN:-false}" == "true" ]]; then
  echo "=== DRY_RUN is enabled. Skipping manifest upload to Exit Gate. ==="
  echo "Artifacts are staged in Artifact Registry."
  exit 0
fi

echo "=== Creating targeted release manifest for google-ads-datamanager-util ==="
cat <<EOF > manifest.json
{
  "publish_all": false,
  "publishing_groups": [
    {
      "packages": [
        {
          "name": "google-ads-datamanager-util"
        }
      ]
    }
  ]
}
EOF

EXIT_GATE_BUCKET="gs://oss-exit-gate-prod-projects-bucket/measurement-devrel/pypi/manifests"
MANIFEST_NAME="manifest-$(date +%Y%m%d%H%M%S).json"

echo "=== Uploading manifest to ${EXIT_GATE_BUCKET}/${MANIFEST_NAME} ==="
gcloud storage cp manifest.json "${EXIT_GATE_BUCKET}/${MANIFEST_NAME}"

echo "========================================================================="
echo "Release successfully triggered! Exit Gate will now verify BCID and publish to PyPI."
echo "========================================================================="
