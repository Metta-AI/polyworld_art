"""Audit the active CharGen library for retired imports and broken selections."""

import ast
import json
from pathlib import Path

import glbs
from pack import inventory
from paths import Library, Scripts, Source
from provenance import LegacyEyes, LegacyParts, validateDocument, validateManifest


def rejected(operation):
  """Require a stale export or pack manifest to fail validation."""
  try:
    operation()
  except ValueError:
    return
  raise AssertionError('Retired content was accepted')


def main():
  """Check runtime dependencies, presets, authoring recipes and stale inputs."""
  manifest = json.loads((Library / 'manifest.json').read_text())
  source = json.loads((Source / 'manifest.json').read_text())
  validateManifest(manifest)
  validateManifest(source)
  clips = {clip['name'] for clip in manifest['clips']}
  assert len(clips) == 43
  assert {clip['name'] for clip in source['clips']} == clips
  parts = inventory(Library, manifest)
  names = {(category, item['name']) for category, _, item in parts.values()}
  assert not set(parts) & LegacyParts
  for catalog in [manifest, source]:
    assert catalog['defaultAnimation'] in clips
    for preset in catalog['presets']:
      assert preset.get('pose', '') in clips | {''}, preset['name']
      for part in preset['parts']:
        if part['item'] not in ['', 'None']:
          assert (part['category'], part['item']) in names, (preset['name'], part)
  files = [path for path in Library.rglob('*.glb')
           if not path.is_relative_to(Source)]
  for path in files:
    document, _ = glbs.read(path)
    validateDocument(document, manifest)
    for image in document.get('images', []):
      assert Path(image.get('uri', '')).stem.lower() not in {
        name.lower() for name in LegacyEyes}, path
  assert {str(path.relative_to(Library))
          for path in (Library / 'animations').rglob('*.glb')} == {
            clip['file'] for clip in manifest['clips']}
  for name in LegacyEyes:
    assert not list((Library / 'eyes').glob(name.lower() + '.*'))
    assert not list((Source / 'eyes').glob(name + '.*'))
  for path in Scripts.glob('*.py'):
    text = path.read_text()
    ast.parse(text, filename=str(path))
    if path == Path(__file__).resolve():
      continue
    assert 'characters/modular_chars' not in text, path
    assert 'Layer Lab/' not in text, path
  for kind in ['pose', 'retargeted']:
    rejected(lambda: validateManifest({
      'clips': [{'name': 'Retired', 'kind': kind}], 'categories': []}))
  for name in LegacyEyes:
    rejected(lambda: validateDocument({
      'nodes': [{'name': 'Eyes_' + name}]}, manifest))
  rejected(lambda: validateDocument({
    'nodes': [], 'animations': [{'name': 'Pose01'}]}, manifest))
  print('VERIFIED', len(files), 'GLBs,', len(parts), 'parts,', len(clips),
        'supported animations, preset dependencies and rejected legacy inputs.')


if __name__ == '__main__':
  main()
