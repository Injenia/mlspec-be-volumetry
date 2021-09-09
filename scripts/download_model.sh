#!/bin/bash
set +x
set +e

current_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Currently only Left model is required
gcs_path=$(python3 -c "import sys, json; print(json.load(open('$current_dir/../src/ml_models/model_info.json'))['model_sx']['gcs_model_path'])")
echo "Download model from $gcs_path"
gsutil cp -r "$gcs_path/*" "$current_dir"/../src/ml_models/model_sx
