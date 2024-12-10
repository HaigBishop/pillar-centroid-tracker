# -*- mode: python -*-

block_cipher = None

from kivy.tools.packaging.pyinstaller_hooks import get_deps_all, hookspath, runtime_hooks
from PyInstaller.utils.hooks import collect_submodules

# Path to your main application script
app_script = 'pillar_centroid_tracker.py'

# Include all files from 'resources' directory
datas = [
    ('resources/*', 'resources')
]

# Gather Kivy dependencies and hooks
hiddenimports = collect_submodules('kivy_deps')

a = Analysis(
    [app_script],
    pathex=['.'],
    binaries=None,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=hookspath(),
    runtime_hooks=runtime_hooks(),
    **get_deps_all()
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='pillar_centroid_tracker',
    debug=False,
    strip=False,
    upx=True,
    console=False
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='pillar_centroid_tracker'
)

app = BUNDLE(
    coll,
    name='pillar_centroid_tracker.app',
    icon='resources/icon.icns',   # Adjust if you prefer a different icon
    bundle_identifier='org.haig.pillarcentroidtracker'
)