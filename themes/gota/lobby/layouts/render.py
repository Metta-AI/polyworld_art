"""Render both transparent layout previews and validate their text styles."""

import json
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

for name in ('battle-setup', 'multiplayer'):
    with tempfile.TemporaryDirectory(prefix='gota-ui-chrome-') as profile:
        completed = subprocess.run(
            [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
             '--allow-file-access-from-files', '--virtual-time-budget=1500',
             '--hide-scrollbars', '--force-device-scale-factor=1',
             '--window-size=1672,941', '--default-background-color=00000000',
             f'--user-data-dir={profile}', f'--screenshot={ROOT / (name + ".png")}',
             '--dump-dom', (ROOT / (name + '.html')).as_uri()],
            check=True,
            capture_output=True,
            text=True,
        )
    match = re.search(
        r'<script id="layout-audit" type="application/json">(.*?)</script>',
        completed.stdout,
    )
    if match is None:
        raise RuntimeError(f'{name}: browser did not produce its layout audit')
    audit = json.loads(match.group(1))
    assert audit['sizes'] == ['20px', '28px', '48px'], audit
    assert audit['fontsLoaded'], audit
    assert not audit['clipped'], audit
    assert not audit['missingImages'], audit
    panels = [bounds for bounds in audit['bounds']
              if bounds['class'].startswith('panel ')
              and 'server-bar' not in bounds['class']]
    assert len(panels) == 2
    assert panels[0]['y'] == panels[1]['y']
    assert panels[0]['height'] == panels[1]['height']
    footer = next(bounds for bounds in audit['bounds']
                  if bounds['class'] == 'footer')
    assert footer['y'] >= panels[0]['y'] + panels[0]['height']
    image = Image.open(ROOT / (name + '.png'))
    assert image.mode == 'RGBA'
    assert image.size == (1672, 941)
    assert image.getchannel('A').getextrema() == (0, 255)
    assert image.getpixel((0, 0))[3] == 0
    audit['image'] = {
        'size': image.size,
        'mode': image.mode,
        'alpha': image.getchannel('A').getextrema(),
        'cornerAlpha': image.getpixel((0, 0))[3],
    }
    (ROOT / (name + '-audit.json')).write_text(
        json.dumps(audit, indent=2) + '\n'
    )
    print(f'{name}: 20/28/48 px, fonts and icons loaded, no clipping, RGBA')
