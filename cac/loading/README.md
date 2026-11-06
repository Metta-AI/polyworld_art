# Cards and Casters loading illustration

`moonlit-table.webp` is the browser's loading background: an archer, warrior
and mage playing cards in a moonlit observatory. The left side stays quiet
for the game's wordmark and progress bar. The portrait layout crops around
the gathering and places the title underneath it.

- `source/moonlit-table.png`: original output from the built-in image generation
  tool, copied without edits on 2026-11-06.
- `moonlit-table.webp`: compressed runtime image, 312,418 bytes (305 KiB).
- `PROMPTS.md`: exact generation prompt; no input images were supplied.

Generate the runtime copy with libwebp's `cwebp`:

```sh
cwebp -quiet -q 86 -m 6 cac/loading/source/moonlit-table.png -o cac/loading/moonlit-table.webp
```

Polyworld's `games/cac/tools/build_web.sh` copies only the WebP into the web
output's `loading/` directory. It stays outside the Wasm game asset pack so
the browser can show it immediately. The original PNG is not packaged.

The vector wordmark and responsive layout live in Polyworld's
`games/cac/web/`. See [asset notices](../../licenses/cac.md) for provenance.
