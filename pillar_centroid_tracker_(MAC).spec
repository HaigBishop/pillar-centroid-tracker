# -*- mode: python -*-

block_cipher = None

from kivy.tools.packaging.pyinstaller_hooks import get_deps_all, hookspath, runtime_hooks
from PyInstaller.utils.hooks import collect_submodules

app_script = 'pillar_centroid_tracker.py'

# Additional data files
extra_datas = [
    ('resources/*', 'resources'),
    ('*.kv', '.')
]

# Get dependencies
deps = get_deps_all()

# Initialize keys to avoid KeyError
deps['datas'] = deps.get('datas', []) + extra_datas
deps['hiddenimports'] = deps.get('hiddenimports', []) + [
    'plyer.platforms.macosx.filechooser',
    'matplotlib.backends.backend_svg',
    'sklearn.tree._partitioner',
    'sklearn.tree._classes',
    'sklearn.manifold._barnes_hut_tsne',
    'sklearn.manifold._quad_tree',
    'sklearn.neighbors._quad_tree',
    'sklearn.cluster._kmeans',
] + collect_submodules('kivy_deps')

a = Analysis(
    [app_script],
    pathex=['.'],
    binaries=deps.get('binaries', []),  # Remove explicit kivy_deps for MacOS
    datas=deps['datas'],
    hiddenimports=deps['hiddenimports'],
    hookspath=hookspath(),
    runtime_hooks=runtime_hooks(),
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    exclude_binaries=True,
    name='pillar_centroid_tracker',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='pillar_centroid_tracker',
)

app = BUNDLE(
    coll,
    name='pillar_centroid_tracker.app',
    icon='resources/icon.icns',
    bundle_identifier='org.haig.pillarcentroidtracker',
    info_plist={
        'CFBundleName': 'Pillar Centroid Tracker',
        'CFBundleDisplayName': 'Pillar Centroid Tracker',
        'CFBundleIdentifier': 'org.haig.pillarcentroidtracker',
        'CFBundleVersion': '1.0.0',
        'CFBundleExecutable': 'pillar_centroid_tracker',
    },
)
