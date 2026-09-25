#!/usr/bin/env bash

set -euo pipefail

show_usage() {
  echo "Usage: contact_sheet.sh [--columns COUNT] [--force] OUTPUT INPUT..."
}

columns=4
force=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --columns)
      [[ $# -ge 2 ]] || { show_usage >&2; exit 1; }
      columns="$2"
      shift 2
      ;;
    --force)
      force=true
      shift
      ;;
    --help|-h)
      show_usage
      exit 0
      ;;
    --*)
      echo "Unknown option: $1" >&2
      show_usage >&2
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

[[ $# -ge 2 ]] || { show_usage >&2; exit 1; }
[[ "$columns" =~ ^[1-9][0-9]*$ ]] || {
  echo "Column count must be a positive integer." >&2
  exit 1
}

output_path="$1"
shift

command -v magick >/dev/null || {
  echo "ImageMagick 7 is required as 'magick'." >&2
  exit 1
}
[[ -d "$(dirname "$output_path")" ]] || {
  echo "Output directory does not exist: $(dirname "$output_path")" >&2
  exit 1
}
if [[ -e "$output_path" && "$force" != true ]]; then
  echo "Output already exists; pass --force to replace it: $output_path" >&2
  exit 1
fi
for input_path in "$@"; do
  [[ -f "$input_path" ]] || {
    echo "Input icon does not exist: $input_path" >&2
    exit 1
  }
done

magick montage "$@" -thumbnail 128x128 \
  -background '#30343b' -fill white -pointsize 14 \
  -set label '%t' -tile "${columns}x" -geometry 144x160+8+8 \
  "$output_path"

echo "Wrote $output_path"
