#!/usr/bin/env bash

set -euo pipefail

show_usage() {
  echo "Usage: cut_icon_sheet.sh [--green] [--grayscale] [--force]"
  echo "  [--size PIXELS] [--content PIXELS] SHEET NAMES_FILE OUTPUT_DIR"
}

green_key=false
grayscale=false
force=false
icon_size=128
content_size=104

while [[ $# -gt 0 ]]; do
  case "$1" in
    --green)
      green_key=true
      shift
      ;;
    --grayscale)
      grayscale=true
      shift
      ;;
    --force)
      force=true
      shift
      ;;
    --size)
      [[ $# -ge 2 ]] || { show_usage >&2; exit 1; }
      icon_size="$2"
      shift 2
      ;;
    --content)
      [[ $# -ge 2 ]] || { show_usage >&2; exit 1; }
      content_size="$2"
      shift 2
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

[[ $# -eq 3 ]] || { show_usage >&2; exit 1; }

sheet_path="$1"
names_path="$2"
output_dir="$3"
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

command -v magick >/dev/null || {
  echo "ImageMagick 7 is required as 'magick'." >&2
  exit 1
}
[[ -f "$sheet_path" ]] || {
  echo "Sheet does not exist: $sheet_path" >&2
  exit 1
}
[[ -f "$names_path" ]] || {
  echo "Names file does not exist: $names_path" >&2
  exit 1
}

names=()
while IFS= read -r name || [[ -n "$name" ]]; do
  [[ -n "$name" ]] || continue
  [[ "$name" =~ ^[a-z0-9]+(_[a-z0-9]+)*$ ]] || {
    echo "Invalid icon base name: $name" >&2
    exit 1
  }
  names+=("$name")
done < "$names_path"

[[ ${#names[@]} -eq 16 ]] || {
  echo "A 4x4 sheet requires exactly 16 non-empty names." >&2
  exit 1
}

mkdir -p "$output_dir"
for name in "${names[@]}"; do
  output_path="$output_dir/$name.png"
  if [[ -e "$output_path" && "$force" != true ]]; then
    echo "Output already exists; pass --force to replace it: $output_path" >&2
    exit 1
  fi
done

sheet_dimensions=$(magick identify -format '%w %h' "$sheet_path")
sheet_width="${sheet_dimensions%% *}"
sheet_height="${sheet_dimensions##* }"
(( sheet_width >= 4 && sheet_height >= 4 )) || {
  echo "Sheet is too small to divide into 4x4 cells." >&2
  exit 1
}

sheet_work=$(mktemp -d "${TMPDIR:-/tmp}/polyworld-sheet.XXXXXX")
cleanup() {
  rm -rf "$sheet_work"
}
trap cleanup EXIT

finish_args=(--size "$icon_size" --content "$content_size")
[[ "$green_key" == true ]] && finish_args+=(--green)
[[ "$grayscale" == true ]] && finish_args+=(--grayscale)
[[ "$force" == true ]] && finish_args+=(--force)

for index in {0..15}; do
  row=$((index / 4))
  column=$((index % 4))
  x0=$((column * sheet_width / 4))
  x1=$(((column + 1) * sheet_width / 4))
  y0=$((row * sheet_height / 4))
  y1=$(((row + 1) * sheet_height / 4))
  cell_width=$((x1 - x0))
  cell_height=$((y1 - y0))
  cell_path="$sheet_work/cell-$index.png"
  output_path="$output_dir/${names[$index]}.png"

  magick "$sheet_path" \
    -crop "${cell_width}x${cell_height}+${x0}+${y0}" +repage \
    "PNG32:$cell_path"
  "$script_dir/finish_icon.sh" "${finish_args[@]}" \
    "$cell_path" "$output_path"
done

echo "Wrote 16 icons to $output_dir"
