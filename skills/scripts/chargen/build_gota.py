"""Rebuild and review isolated Gota modules after the shared character library."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from paths import Source, Preview
from register_gota import Order


def main():
  """Run separate builders sequentially and preserve the existing master file."""
  parser=argparse.ArgumentParser()
  parser.add_argument('--hero',choices=Order)
  parser.add_argument('--render',action='store_true')
  args=parser.parse_args()
  scripts=Path(__file__).resolve().parent
  blender=os.environ.get('BLENDER','/Applications/Blender.app/Contents/MacOS/Blender')
  selected=[args.hero] if args.hero else Order
  def build(script,*arguments):
    """Run one authoring command with failure propagation."""
    command=[blender,'-b','--python-exit-code','1','--python',str(scripts/script)]
    if arguments:command+=['--',*arguments]
    subprocess.run(command,check=True)
  build('build_gota_body.py')
  for slug in selected:
    build('gota_common.py',slug)
    build('finalize_gota.py',slug)
    if args.render:
      env=dict(os.environ,CHARGEN_LIBRARY=str(Preview/'gota'/slug/'library'),
               REVIEW_OUTPUT=str(Source/'gota'/slug/'renders'))
      subprocess.run([str(Preview/'gota/render_gota')],env=env,check=True)
      subprocess.run([sys.executable,str(scripts/'review_gota.py'),slug],check=True)
  subprocess.run([sys.executable,str(scripts/'register_gota.py')],check=True)
  subprocess.run([sys.executable,str(scripts/'verify_gota.py')],check=True)


if __name__=='__main__':main()
