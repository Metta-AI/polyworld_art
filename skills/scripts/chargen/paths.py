"""Resolve bundled recipes against an explicit or neighboring art library."""

import os
from pathlib import Path

Scripts = Path(__file__).resolve().parent
Data = Path(os.environ.get('CHARGEN_ART', Scripts.parents[2])).resolve()
Library = Path(os.environ.get(
  'CHARGEN_LIBRARY', Data / 'characters/chargen')).resolve()
Source = Library / 'source'
Project = Path(os.environ.get(
  'POLYWORLD_PROJECT', Data.parent / 'polyworld')).resolve()
Preview = Path(os.environ.get(
  'CHARGEN_PREVIEW', Project / 'tmp/chargen')).resolve()
