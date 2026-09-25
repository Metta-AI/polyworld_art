#!/usr/bin/env bash

set -euo pipefail

show_usage() {
  echo "Usage: finish_icon.sh [--green] [--grayscale] [--crop GEOMETRY]"
  echo "  [--size PIXELS] [--content PIXELS] [--force] INPUT OUTPUT"
}

green_key=false
grayscale=false
force=false
crop_geometry=""
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
    --crop)
      [[ $# -ge 2 ]] || { show_usage >&2; exit 1; }
      crop_geometry="$2"
      shift 2
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

[[ $# -eq 2 ]] || { show_usage >&2; exit 1; }

input_path="$1"
output_path="$2"

command -v magick >/dev/null || {
  echo "ImageMagick 7 is required as 'magick'." >&2
  exit 1
}
[[ -f "$input_path" ]] || {
  echo "Input icon does not exist: $input_path" >&2
  exit 1
}
[[ "$icon_size" =~ ^[0-9]+$ ]] || {
  echo "Icon size must be a positive integer." >&2
  exit 1
}
[[ "$content_size" =~ ^[0-9]+$ ]] || {
  echo "Content size must be a positive integer." >&2
  exit 1
}
(( icon_size > 0 && content_size > 0 && content_size <= icon_size )) || {
  echo "Content size must be between 1 and the icon size." >&2
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

icon_work=$(mktemp -d "${TMPDIR:-/tmp}/polyworld-icon.XXXXXX")
cleanup() {
  rm -rf "$icon_work"
}
trap cleanup EXIT

source_path="$input_path"
if [[ -n "$crop_geometry" ]]; then
  source_path="$icon_work/cropped.png"
  magick "$input_path" -crop "$crop_geometry" +repage \
    "PNG32:$source_path"
fi

raw_path="$icon_work/raw.png"
if [[ "$green_key" == true ]]; then
  mask_path="$icon_work/alpha.png"
  keyed_path="$icon_work/keyed.png"
  magick "$source_path" -alpha off \
    -fx 'max(0,min(1,1-(g-max(r,b))/0.35))' "$mask_path"
  magick "$source_path" "$mask_path" -alpha off \
    -compose CopyOpacity -composite "PNG32:$keyed_path"
  magick "$keyed_path" -channel G \
    -fx 'min(g,max(r,b))' +channel "PNG32:$raw_path"
else
  channels=$(magick identify -format '%[channels]' "$source_path")
  if [[ "$channels" != *a* ]]; then
    echo "Input has no alpha. Pass --green for a chroma-green source." >&2
    exit 1
  fi
  magick "$source_path" "PNG32:$raw_path"
fi

max_alpha=$(magick "$raw_path" -alpha extract \
  -format '%[fx:maxima]' info:)
if awk -v alpha="$max_alpha" 'BEGIN { exit !(alpha <= 0) }'; then
  echo "The processed source has no visible pixels." >&2
  exit 1
fi

final_path="$icon_work/final.png"
if [[ "$grayscale" == true ]]; then
  magick "$raw_path" -colorspace Gray -colorspace sRGB \
    -trim +repage -resize "${content_size}x${content_size}" \
    -gravity center -background none -extent "${icon_size}x${icon_size}" \
    "PNG32:$final_path"
else
  magick "$raw_path" -trim +repage \
    -resize "${content_size}x${content_size}" \
    -gravity center -background none -extent "${icon_size}x${icon_size}" \
    "PNG32:$final_path"
fi

if [[ "$green_key" == true && "$grayscale" != true ]]; then
  clean_path="$icon_work/clean.png"
  magick "$final_path" -channel G \
    -fx 'min(g,max(r,b))' +channel "PNG32:$clean_path"
  mv "$clean_path" "$final_path"
fi

dimensions=$(magick identify -format '%wx%h' "$final_path")
[[ "$dimensions" == "${icon_size}x${icon_size}" ]] || {
  echo "Unexpected output dimensions: $dimensions" >&2
  exit 1
}
opaque=$(magick identify -format '%[opaque]' "$final_path")
[[ "$opaque" == "False" ]] || {
  echo "Output does not contain transparency." >&2
  exit 1
}

mv "$final_path" "$output_path"
echo "Wrote $output_path"
