"""Shared locations for character authoring and the sibling Nim preview tool."""

from pathlib import Path

Scripts = Path(__file__).resolve().parent
Source = Scripts.parent
Library = Source.parent
Data = Library.parents[1]
Project = Data.parent / 'polyworld'
Preview = Project / 'tmp/chargen'
