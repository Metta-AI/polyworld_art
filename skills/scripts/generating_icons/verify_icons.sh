#!/usr/bin/env bash

set -euo pipefail

show_usage() {
  echo "Usage: verify_icons.sh [--grayscale] [--size PIXELS] ICON..."
}

require_grayscale=false
icon_size=128

while [[ $# -gt 0 ]]; do
  case "$1" in
    --grayscale)
      require_grayscale=true
      shift
      ;;
    --size)
      [[ $# -ge 2 ]] || { show_usage >&2; exit 1; }
      icon_size="$2"
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

[[ $# -ge 1 ]] || { show_usage >&2; exit 1; }
[[ "$icon_size" =~ ^[1-9][0-9]*$ ]] || {
  echo "Icon size must be a positive integer." >&2
  exit 1
}
command -v magick >/dev/null || {
  echo "ImageMagick 7 is required as 'magick'." >&2
  exit 1
}

failures=0
checked=0

fail_icon() {
  echo "$1: $2" >&2
  failures=$((failures + 1))
}

for icon_path in "$@"; do
  checked=$((checked + 1))
  if [[ ! -f "$icon_path" ]]; then
    fail_icon "$icon_path" "file does not exist"
    continue
  fi
  if [[ "${icon_path##*.}" != png ]]; then
    fail_icon "$icon_path" "expected a .png file"
    continue
  fi

  dimensions=$(magick identify -format '%w %h' "$icon_path")
  width="${dimensions%% *}"
  height="${dimensions##* }"
  if [[ "$width" -ne "$icon_size" || "$height" -ne "$icon_size" ]]; then
    fail_icon "$icon_path" \
      "expected ${icon_size}x${icon_size}, found ${width}x${height}"
  fi

  channels=$(magick identify -format '%[channels]' "$icon_path")
  if [[ "$channels" != *a* ]]; then
    fail_icon "$icon_path" "PNG has no alpha channel"
  fi

  last_pixel=$((icon_size - 1))
  for corner in \
    "0,0" "$last_pixel,0" \
    "0,$last_pixel" "$last_pixel,$last_pixel"; do
      corner_alpha=$(magick "$icon_path" \
        -format "%[fx:p{$corner}.a]" info:)
      if ! awk -v alpha="$corner_alpha" \
        'BEGIN { exit !(alpha == 0) }'; then
        fail_icon "$icon_path" \
          "corner $corner is not transparent"
      fi
  done

  max_alpha=$(magick "$icon_path" -alpha extract \
    -format '%[fx:maxima]' info:)
  if awk -v alpha="$max_alpha" 'BEGIN { exit !(alpha <= 0) }'; then
    fail_icon "$icon_path" "icon has no visible pixels"
    continue
  fi

  bounds=$(magick "$icon_path" -alpha extract -threshold 3% \
    -format '%@' info:)
  if [[ "$bounds" =~ ^([0-9]+)x([0-9]+)\+([0-9]+)\+([0-9]+)$ ]]; then
    visible_width="${BASH_REMATCH[1]}"
    visible_height="${BASH_REMATCH[2]}"
    x_offset="${BASH_REMATCH[3]}"
    y_offset="${BASH_REMATCH[4]}"
    expected_x=$(((icon_size - visible_width) / 2))
    expected_y=$(((icon_size - visible_height) / 2))
    x_delta=$((x_offset - expected_x))
    y_delta=$((y_offset - expected_y))
    if (( x_delta < 0 )); then
      x_delta=$((-x_delta))
    fi
    if (( y_delta < 0 )); then
      y_delta=$((-y_delta))
    fi
    if (( x_delta > 1 || y_delta > 1 )); then
      fail_icon "$icon_path" "visible pixels are not centered: $bounds"
    fi
  else
    fail_icon "$icon_path" "could not read visible bounds: $bounds"
  fi

  markdown_path="${icon_path%.png}.md"
  if [[ ! -f "$markdown_path" ]]; then
    fail_icon "$icon_path" "missing companion Markdown: $markdown_path"
  fi

  if [[ "$require_grayscale" == true ]]; then
    rgb_delta=$(magick "$icon_path" -channel RGB \
      -fx 'abs(r-g)+abs(g-b)+abs(b-r)' \
      -format '%[fx:maxima]' info:)
    if ! awk -v delta="$rgb_delta" \
      'BEGIN { exit !(delta <= 0.001) }'; then
      fail_icon "$icon_path" "visible RGB is not neutral grayscale"
    fi
  fi
done

if (( failures > 0 )); then
  echo "Found $failures issue(s) in $checked icon(s)." >&2
  exit 1
fi

echo "Validated $checked icon(s)."
