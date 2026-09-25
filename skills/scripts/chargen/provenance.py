"""Keep retired character imports out of authoring exports and game packs."""

LegacyEyes = {'Neutral', 'Happy', 'Angry', 'Original2'}
LegacyNodes = {'Eyes_' + name for name in LegacyEyes}
LegacyParts = {'eyes/' + name.lower() for name in LegacyEyes}


def validatePart(item):
  """Reject known retired eye variants before reading their asset files."""
  if item.get('id') in LegacyParts or any(
      node in LegacyNodes or node.startswith('QuickRigCharacter2_')
      for node in item.get('nodes', [])):
    raise ValueError('Retired character part: ' + item['name'])


def validateManifest(manifest):
  """Require the supported clip source and exclude imported eye selections."""
  for clip in manifest['clips']:
    if clip.get('kind') != 'universal':
      raise ValueError('Unsupported animation source: ' + clip['name'])
  for category in manifest['categories']:
    for item in category.get('items', []):
      validatePart(item)


def validateDocument(document, manifest):
  """Refuse stale mixed Blender exports before writing any runtime assets."""
  validateManifest(manifest)
  for node in document['nodes']:
    name = node.get('name', '')
    if name in LegacyNodes or name.startswith('QuickRigCharacter2_'):
      raise ValueError('Retired character node in authoring export: ' + name)
  allowed = {clip['name'] for clip in manifest['clips']}
  for clip in document.get('animations', []):
    if clip['name'] not in allowed:
      raise ValueError('Unsupported clip in authoring export: ' + clip['name'])
