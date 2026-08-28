#!/usr/bin/env bash

set -e

artifact_name="$1"
artifact_path="tmp/${artifact_name}.json"
mkdir -p "$(dirname "$artifact_path")"
printf '{"name":"%s"}\n' "$artifact_name" > "$artifact_path"
echo "artifact-path=$artifact_path" >> "$GITHUB_OUTPUT"
