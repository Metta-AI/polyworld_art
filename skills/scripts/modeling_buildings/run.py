"""Stage the preserved workflow scripts into an explicit working directory."""

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

Scripts = Path(__file__).resolve().parent
Groups = ('buildings', 'faction_trims', 'faction_renders')
PythonScripts = {'externalize_textures.py', 'update_glb_atlas.py', 'package.py', 'compose.py'}
NeedsScene = {'build_construction.py', 'export_glbs.py', 'export_construction.py',
  'finalize_scene.py', 'rescale_buildings.py', 'restore_cart.py', 'revise_scene.py',
  'verify_scene.py', 'verify_glbs.py', 'verify_construction.py'}
NeedsPack = {'externalize_textures.py', 'update_glb_atlas.py', 'verify_shared_atlas.py',
  'package.py', 'render_preview.py', 'render_all.py', 'compose.py'}
RenderOnly = {'render_preview.py', 'render_all.py'}

def main():
  """Copy one script group and run its selected entry point."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('workflow', choices=Groups)
  parser.add_argument('script', help='A bundled .py or .nim filename.')
  parser.add_argument('--work', type=Path, required=True,
    help='Explicit workspace for scripts, inputs, blends and generated outputs.')
  parser.add_argument('--pack', type=Path,
    help='Asset pack to read or update; only required by pack-oriented scripts.')
  parser.add_argument('--scene', type=Path,
    help='Blend file to load first; relative paths are resolved inside --work.')
  parser.add_argument('--blender', default=shutil.which('blender') or
    ('/Applications/Blender.app/Contents/MacOS/Blender' if sys.platform == 'darwin' else 'blender'))
  parser.add_argument('--threads', type=int, default=6)
  parser.add_argument('--skip-render', action='store_true',
    help='Skip optional PNG previews during modeling or validation.')
  parser.add_argument('--final', action='store_true', help='Use build_scene.py final render quality.')
  parser.add_argument('--polyworld', type=Path,
    help='Game repository supplying src/polyworld for the optional Nim loader checks.')
  parser.add_argument('--refresh-scripts', action='store_true',
    help='Replace differing staged scripts. Assets and blends are never copied by the launcher.')
  parser.add_argument('--dry-run', action='store_true',
    help='Print paths and commands without staging or executing anything.')
  args = parser.parse_args()
  group = Scripts / args.workflow
  source = group / args.script
  if Path(args.script).name != args.script or not source.is_file() or source.suffix not in ('.py', '.nim'):
    parser.error('Choose a bundled .py or .nim filename from ' + str(group))
  work = args.work.expanduser().resolve()
  if work == Scripts or Scripts in work.parents or work in Scripts.parents:
    parser.error('--work must be separate from the bundled scripts and their parent directories.')
  if args.script in NeedsScene and args.scene is None:
    parser.error(args.script + ' needs --scene; see the documented rebuild order.')
  if args.script in NeedsPack and args.pack is None:
    parser.error(args.script + ' needs an explicit --pack.')
  if args.pack is not None and args.script not in NeedsPack:
    parser.error(args.script + ' does not use --pack; exporters write under --work.')
  if args.scene is not None and args.script not in NeedsScene:
    parser.error(args.script + ' does not use a preloaded --scene.')
  if args.final and args.script != 'build_scene.py':
    parser.error('--final only applies to build_scene.py.')
  if args.polyworld is not None and source.suffix != '.nim':
    parser.error('--polyworld only applies to the Nim loader checks.')
  if args.skip_render and (args.workflow != 'buildings' or args.script in RenderOnly):
    parser.error('--skip-render is only for optional building-workflow previews.')
  if args.threads < 1:
    parser.error('--threads must be positive.')
  scene = (work / args.scene.expanduser()).resolve() if args.scene else None
  if scene and not scene.is_file():
    parser.error('Blend file does not exist: ' + str(scene))
  pack = args.pack.expanduser().resolve() if args.pack else None
  staged = work / args.script
  if source.suffix == '.nim':
    if args.polyworld is None:
      parser.error('The Nim loader checks need --polyworld pointing to the game repository.')
    gameSource = args.polyworld.expanduser().resolve() / 'src'
    if not (gameSource / 'polyworld/quadterrain.nim').is_file():
      parser.error('Cannot find polyworld/quadterrain.nim under ' + str(gameSource))
    flags = ['--path:' + str(gameSource), '--nimcache:' + str(work / 'nimcache')]
    commands = [['nim', 'check', *flags, str(staged)],
      ['nim', 'r', *flags, '--out:' + str(work / 'bin' / source.stem), str(staged)]]
  elif args.script in PythonScripts:
    commands = [[sys.executable, str(staged)]]
  else:
    blender = args.blender
    if os.path.dirname(blender):
      blender = str(Path(blender).expanduser().resolve())
    command = [blender, '-b'] + ([str(scene)] if scene else [])
    command += ['--threads', str(args.threads), '--python-exit-code', '1', '--python', str(staged)]
    if args.final:
      command += ['--', '--final']
    commands = [command]
  print(json.dumps({'workspace': str(work), 'pack': str(pack) if pack else None,
    'commands': [shlex.join(command) for command in commands]}, indent=2), flush=True)
  if args.dry_run:
    return
  files = [path for path in sorted(group.iterdir()) if path.suffix in ('.py', '.nim', '.html')]
  for path in files:
    target = work / path.name
    if target.exists() and target.read_bytes() != path.read_bytes() and not args.refresh_scripts:
      parser.error('Staged script differs: ' + str(target) + '. Preserve edits or use --refresh-scripts.')
  for directory in ['', 'assets', 'reviews', 'renders', 'exports', 'versions', 'bin']:
    (work / directory).mkdir(parents=True, exist_ok=True)
  for path in files:
    shutil.copy2(path, work / path.name)
  environment = os.environ.copy()
  if pack:
    environment['POLYWORLD_BUILDING_PACK'] = str(pack)
  else:
    environment.pop('POLYWORLD_BUILDING_PACK', None)
  if args.skip_render:
    environment['POLYWORLD_BUILDINGS_SKIP_RENDER'] = '1'
  else:
    environment.pop('POLYWORLD_BUILDINGS_SKIP_RENDER', None)
  for command in commands:
    subprocess.run(command, cwd=work, env=environment, check=True)

if __name__ == '__main__':
  main()
