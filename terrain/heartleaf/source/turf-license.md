# Heartleaf meadow turf

Creator: Softmax / Polyworld contributors with Codex and built-in imagegen.
Created: 2026-09-25. License: CC0-1.0 under the repository LICENSE.

This is original AI-generated grass and clover artwork. The aligned height map
was generated using the new color master as its only image input. No Unity or
third-party textures were used. The prompts, master dimensions and processing
steps are recorded in turf-provenance.json. Both original tool outputs and
seam-corrected masters are preserved alongside it.

The terrain skill's Nim/Pixie tools corrected a narrow edge band, exported the
paired 256 by 256 textures and verified opaque pixels and matching tile edges.
The runtime uses these files for Heartleaf's grass, cottage banks and woodland
floor. Code applies small regional color tints without changing their provenance.
