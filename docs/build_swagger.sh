#!/usr/bin/env bash

set -eux

SWAGGER_VERSION="4.15.5"
TARGET_PATH=${TARGET_PATH-"swagger"}

rm -rf "$TARGET_PATH" /tmp/swagger-ui
git clone --branch="v$SWAGGER_VERSION" --depth=1 "https://github.com/swagger-api/swagger-ui.git" /tmp/swagger-ui

mv /tmp/swagger-ui/dist "$TARGET_PATH"
sed -i "s#https://petstore.swagger.io/v2/swagger.json#https://dev.funkwhale.audio/funkwhale/funkwhale/-/jobs/artifacts/$CI_COMMIT_BRANCH/raw/docs/schema.yml?job=build_openapi_schema#g" "$TARGET_PATH/swagger-initializer.js"
