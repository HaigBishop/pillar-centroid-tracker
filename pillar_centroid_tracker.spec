# -*- mode: python -*-

block_cipher = None

from kivy.tools.packaging.pyinstaller_hooks import get_deps_all, hookspath, runtime_hooks
from PyInstaller.utils.hooks import collect_submodules

app_script = 'pillar_centroid_tracker.py'

# Additional data to include
extra_datas = [
    ('resources/*', 'resources')
]

# Get Kivy dependencies
deps = get_deps_all()  # returns dict with keys: binaries, datas, hiddenimports
# Add our extra data to the existing datas from get_deps_all()
deps['datas'] += extra_datas

# If you want extra hidden imports, do that as well
deps['hiddenimports'] += collect_submodules('kivy_deps')

a = Analysis(
    [app_script],
    pathex=['.'],
    **deps
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
    icon='resources/icon.icns',
    bundle_identifier='org.haig.pillarcentroidtracker'
)