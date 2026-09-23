# Contributing art

All artwork accepted here must remain free to use, modify and redistribute,
including for commercial purposes. Prefer CC0 for new original artwork.
The current accepted licenses are CC0-1.0, CC-BY-4.0, MIT and OFL-1.1.
An additional open license needs an explicit maintainer review of its terms
before the allowlist changes. Do not silently label third-party work CC0.

For every new asset or changed asset:

1. Record the creator, title, original source, license and modifications.
   For project-generated work, record the creation process and any inputs.
   You must have the rights to contribute it under the stated license.
2. Preserve the complete applicable notices. Check embedded textures, rigs,
   animations, fonts, reference images and other dependencies too.
3. Add or update its entry in `licenses/assets.json`, including SHA-256,
   byte size, source record and the correct SPDX license identifier.
   Retain source links and attribution for third-party derivatives.
4. Add binary formats to `.gitattributes` before staging them, then use
   `git lfs install --local` and `git add` normally.
5. Run the checks listed in the README and inspect the staged diff.

Never add Unity Asset Store packs, proprietary assets, assets restricted to
noncommercial or personal use, engine-only assets, or material whose origin
is unclear. Do not import legacy Git history or archives containing excluded
files. Old renders can contain restricted components even after a model has
been cleaned. Treat them as separate assets requiring their own review.

By contributing original artwork under CC0, you make the same permanent
dedication as the project. Authoring and validation code uses `LICENSE-CODE`.
Third-party contributions retain their documented licenses. Do not impose
additional restrictions on copies already distributed under open terms.

Maintainers must review the source record and binary changes, not just accept
updated hashes.
