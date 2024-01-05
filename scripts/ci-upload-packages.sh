#!/usr/bin/env bash

# Make sure that https://docs.gitlab.com/ee/user/packages/generic_packages/#do-not-allow-duplicate-generic-packages
# is enabled

set -eu

error() {
  echo >&2 "error: $*"
  exit 1
}

command -v curl > /dev/null || error "curl command not found!"

PACKAGE_REGISTRY_URL="$CI_API_V4_URL/projects/$CI_PROJECT_ID/packages/generic"
PACKAGE_NAME="funkwhale"
PACKAGE_VERSION="$CI_COMMIT_REF_NAME"

join_by() {
  local IFS="$1"
  shift
  echo "$*"
}

# publish_asset <asset> <file>
publish_asset() {
  echo "publishing release asset $asset"
  curl \
    --fail \
    --show-error \
    --header "JOB-TOKEN: $CI_JOB_TOKEN" \
    --upload-file "$2" \
    "$PACKAGE_REGISTRY_URL/$PACKAGE_NAME/$PACKAGE_VERSION/$1"
  echo
}

# release_asset_json <asset>
release_asset_json() {
  printf '{"name": "%s", "url": "%s", "link_type": "package"}' \
    "$1" \
    "$PACKAGE_REGISTRY_URL/$PACKAGE_NAME/$PACKAGE_VERSION/$1"
}

# release_json <release_assets_json>
release_json() {
  printf '{"name": "%s", "tag_name": "%s", "assets": { "links": [%s]}}' "$PACKAGE_VERSION" "$PACKAGE_VERSION" "$1"
}

release_assets=()
for asset_path in dist/*; do
  asset="$(basename "$asset_path")"
  publish_asset "$asset" "$asset_path"
  release_assets+=("$(release_asset_json "$asset")")
done
