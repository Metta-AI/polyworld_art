# Polyworld Art

Freely reusable art for Gods of the Arena, Call to Adventure, and Light vs Dark.
This repository starts with a new history and contains a curated snapshot of
cleared assets. It does not inherit the old asset repository's Git history.

**This art must stay free to use, study, modify, and redistribute, including
commercially.** Original project artwork is dedicated to the public domain
under [CC0 1.0](LICENSE). Third-party work keeps its documented open license.
No Unity Asset Store content, noncommercial assets, engine-only licenses,
personal-use-only assets, or assets with unresolved provenance belong here.
Being free to download is not enough.

**The repository is private during preparation. Keep it private until the
owner explicitly authorizes publication.** The open licenses describe reuse
rights in the files. They do not mean the repository is already public.

## Free now and in the future

The CC0 dedication is permanent. We will not withdraw the freedoms granted
for released copies or replace their open terms with proprietary restrictions.
Future contributions to this repository must meet the same free-use policy.
Preserve attribution and license notices wherever the applicable license
requires them. We do not claim ownership of third-party artwork.

CC0 permits commercial use and proprietary derivatives. It does not require
other people's modifications to be published, and this README adds no such
restriction. Our commitment is that the assets maintained here remain freely
reusable under their stated terms.

## Licenses

| Material | License | Required notice |
| --- | --- | --- |
| Project-generated models, textures, portraits, icons, UI and logos | CC0-1.0 | [Dedication and full terms](LICENSE) |
| Quaternius Universal Standard animations and retargeted clips | CC0-1.0 | [Source and license](animations/quaternius/universal_standard/README.txt) |
| Three.js water normal maps | MIT | [Copyright and full terms](terrain/water_normals/license.md) |
| Rubik, Overpass Mono and IBM Plex Sans fonts | OFL-1.1 | [Font notices](fonts/license.md) |
| Authoring and validation source code | MIT | [Code license](LICENSE-CODE) |

The CC0 default never overrides another creator's license. Font-derived
glyphs keep their font license, including when packed into an atlas.
The [per-file inventory](licenses/assets.json) records each file's license,
source, notice, SHA-256 digest and size. See [PROVENANCE.md](PROVENANCE.md)
for the import scope and exclusions, and the [contribution rules](CONTRIBUTING.md)
before adding or changing assets.

## Clone with Git LFS

Install [Git LFS](https://git-lfs.com/) before cloning. Binary art has used
GitHub's Git LFS storage from the first commit. Models, editable Blender
files, textures, images and fonts are stored as LFS objects. Text recipes,
manifests, source code and license notices stay in regular Git.

Clone this repository beside `polyworld`:

```sh
git lfs install
git clone git@github.com:metta-ai/polyworld_art.git
git -C polyworld_art lfs pull
```

The games load `../polyworld_art` when run from the `polyworld` directory.
Browser builds mount selected assets at `/polyworld_art`. The optional
`POLYWORLD_ART` environment variable selects the browser build's source
directory. A private clone requires authorized GitHub access.

## Verify a checkout

```sh
python3 -m pip install Pillow==12.3.0
python3 tools/verify_assets.py
python3 characters/chargen/source/scripts/verify_clean.py
git lfs fsck
```

The checks reject missing or unregistered files, changed content without
updated provenance, unsupported licenses, missing notices, known retired
asset families, and binary assets committed outside LFS. CI runs these checks
on pushes and pull requests. Maintainers must still review provenance because
a checksum or automated check cannot establish an asset's legal origin.

Heartleaf and AWM assets are outside this migration and are not included.
