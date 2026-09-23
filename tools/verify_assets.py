"""Verify the reviewed asset inventory, notices and Git LFS storage."""

import hashlib
import json
import subprocess
from pathlib import Path, PurePosixPath

Root = Path(__file__).resolve().parents[1]
Allowed = {'CC0-1.0', 'CC-BY-4.0', 'MIT', 'OFL-1.1'}
Controls = {
  '.gitattributes', '.gitignore', '.github/workflows/assets.yml',
  'README.md', 'CONTRIBUTING.md', 'PROVENANCE.md', 'LICENSE', 'LICENSE-CODE',
  'licenses/assets.json', 'tools/verify_assets.py',
}
Retired = (
  'characters/mini_legion/', 'characters/modular_chars/',
  'characters/rpg_monsters/', 'terrain/handpainted_trees/',
  'terrain/cartoon_textures/', 'terrain/toon_enchanted_meadow/',
  'terrain/toon_golden_valley/', 'terrain/tower_defense_kit',
  'awm/', 'cogcraft/', 'sounds/', 'themes/heartleaf/',
)
BinaryTypes = {
  '.png', '.jpg', '.jpeg', '.webp', '.gif', '.tga', '.exr', '.hdr',
  '.psd', '.kra', '.glb', '.bin', '.fbx', '.blend', '.ttf', '.otf',
  '.woff', '.woff2', '.wav', '.ogg', '.mp3', '.mp4', '.webm', '.ktx2', '.zip',
}

def require(condition, message):
  """Raise a descriptive error instead of relying on removable assertions."""
  if not condition:
    raise ValueError(message)

def checkedPath(name):
  """Reject paths that escape the repository or traverse symlinks."""
  path = PurePosixPath(name)
  require(bool(name) and not path.is_absolute() and '..' not in path.parts
          and '\\' not in name and str(path) == name, 'Invalid path: ' + name)
  local = Root / name
  require(not any(part.is_symlink() for part in [local, *local.parents]),
          'Symlink in asset path: ' + name)
  return local

def git(*arguments, inputData=None):
  """Run a checked Git query against this repository."""
  return subprocess.run(
    ['git', '-C', str(Root), *arguments], input=inputData,
    stdout=subprocess.PIPE, check=True,
  ).stdout

def main():
  """Check each tracked asset against its reviewed provenance and LFS pointer."""
  catalog = json.loads((Root / 'licenses/assets.json').read_text())
  require(catalog['version'] == 1, 'Unsupported inventory version')
  entries = catalog['files']
  names = [entry['path'] for entry in entries]
  require(len(names) == len(set(names)), 'Duplicate inventory paths')
  tracked = set(git('ls-files', '-z').decode().rstrip('\0').split('\0'))
  require(tracked == set(names) | Controls,
          'Unregistered or missing files: ' +
          ', '.join(sorted(tracked ^ (set(names) | Controls))))
  sources = catalog['sources']
  binaries = []
  for entry in entries:
    name = entry['path']
    path = checkedPath(name)
    require(not name.startswith(Retired), 'Retired asset family: ' + name)
    require(path.is_file(), 'Missing asset: ' + name)
    require(entry['license'] in Allowed, 'Unsupported license: ' + name)
    require(entry['source'] in sources, 'Missing source record: ' + name)
    source = sources[entry['source']]
    require(entry['license'] == source['license'], 'Source license mismatch: ' + name)
    for field in ['creator', 'title', 'origin', 'changes', 'notice']:
      require(bool(source.get(field)), 'Incomplete source record: ' + name)
    require(checkedPath(source['notice']).is_file(), 'Missing notice: ' + name)
    data = path.read_bytes()
    require(not data.startswith(b'version https://git-lfs.github.com/spec/v1'),
            'LFS content missing, run git lfs pull: ' + name)
    require(len(data) == entry['bytes'], 'Changed asset size: ' + name)
    require(hashlib.sha256(data).hexdigest() == entry['sha256'],
            'Changed asset digest: ' + name)
    binary = path.suffix.lower() in BinaryTypes or b'\0' in data[:8192]
    if binary:
      binaries.append(entry)
  paths = '\0'.join(entry['path'] for entry in binaries) + '\0'
  attributes = git('check-attr', '--cached', '-z', '--stdin', 'filter',
                   inputData=paths.encode()).decode().split('\0')
  filters = dict(zip(attributes[0::3], attributes[2::3]))
  references = ''.join(':' + entry['path'] + '\n' for entry in binaries).encode()
  headers = git('cat-file', '--batch-check', inputData=references).splitlines()
  require(len(headers) == len(binaries), 'Missing staged binary objects')
  for entry, header in zip(binaries, headers):
    fields = header.split()
    require(len(fields) == 3 and fields[1] == b'blob' and int(fields[2]) < 1024,
            'Staged binary is not an LFS pointer: ' + entry['path'])
  pointers = git('cat-file', '--batch', inputData=references)
  offset = 0
  for entry in binaries:
    name = entry['path']
    require(filters.get(name) == 'lfs', 'LFS rule missing: ' + name)
    end = pointers.index(b'\n', offset)
    size = int(pointers[offset:end].split()[2])
    actual = pointers[end + 1:end + 1 + size]
    offset = end + size + 2
    expected = ('version https://git-lfs.github.com/spec/v1\n'
                'oid sha256:' + entry['sha256'] + '\n'
                'size ' + str(entry['bytes']) + '\n').encode()
    require(actual == expected,
            'Staged LFS pointer does not match reviewed content: ' + name)
  print('Verified', len(entries), 'files, source records, open licenses and LFS pointers.')

if __name__ == '__main__':
  main()
