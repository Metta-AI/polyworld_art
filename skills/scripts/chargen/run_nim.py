"""Run the live Chargen Nim utilities with their project configuration."""

import argparse
import os
import shlex
import subprocess

from paths import Library, Preview, Project


def main():
  """Choose a bundled tool name and compile its current project source."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('tool', choices=[
    'chargen', 'render_garments', 'render_hats', 'render_gota',
    'render_swords', 'tests'])
  parser.add_argument('--check', action='store_true')
  parser.add_argument('--compile-only', action='store_true')
  parser.add_argument('--dry-run', action='store_true')
  args = parser.parse_args()
  source = Project / 'experiments/chargen' / (args.tool + '.nim')
  if not source.is_file():
    parser.error('Missing live tool: ' + str(source))
  output = Preview / 'skill_tools'
  command = ['nim', 'check' if args.check else 'c']
  if not args.check:
    if not args.compile_only:
      command.append('-r')
    command.extend(['--nimcache:' + str(output / ('cache_' + args.tool)),
                    '-o:' + str(output / args.tool)])
  command.append(str(source))
  print('Working directory:', Project, flush=True)
  print(shlex.join(command), flush=True)
  if args.dry_run:
    return
  if not args.check:
    output.mkdir(parents=True, exist_ok=True)
  environment = dict(os.environ, CHARGEN_LIBRARY=str(Library))
  subprocess.run(command, cwd=Project, env=environment, check=True)


if __name__ == '__main__':
  main()
