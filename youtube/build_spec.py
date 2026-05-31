#!/usr/bin/env python3
"""Self-generated PyInstaller spec — includes ALL yt_dlp submodules."""
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.building.api import Analysis, PYZ, EXE, BUNDLE
import subprocess
import os
import yt_dlp

# === Discover ALL yt_dlp submodules ===
yt_dlp_dir = os.path.dirname(yt_dlp.__file__)
hidden_imports = []
for root, dirs, files in os.walk(yt_dlp_dir):
    if '__pycache__' in root or '.pyc' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            rel = os.path.relpath(os.path.join(root, f), yt_dlp_dir)
            module_name = rel.replace(os.sep, '.').replace('.py', '')
            if module_name:
                hidden_imports.append(module_name)
    for d in dirs:
        init = os.path.join(root, d, '__init__.py')
        if os.path.isfile(init) and '__pycache__' not in d:
            rel = os.path.relpath(os.path.join(root, d), yt_dlp_dir)
            hidden_imports.append(rel.replace(os.sep, '.'))

hidden_imports = sorted(set(hidden_imports))
print(f"Discovered {len(hidden_imports)} yt_dlp submodules")

# === ffmpeg path ===
def _get_path(cmd):
    try:
        p = subprocess.run([cmd], capture_output=True, text=True, timeout=3)
        if p.returncode == 0 and p.stdout.strip():
            return os.path.realpath(p.stdout.strip())
    except Exception:
        pass
    return None

_ffmpeg_path = _get_path('ffmpeg') or '/opt/homebrew/Cellar/ffmpeg/8.1.1/bin/ffmpeg'
_ffprobe_path = _get_path('ffprobe')
if not _ffprobe_path and _ffmpeg_path:
    _ffprobe_path = os.path.join(os.path.dirname(_ffmpeg_path), 'ffprobe')
    if not os.path.isfile(_ffprobe_path):
        _ffprobe_path = os.path.join(os.path.dirname(os.path.dirname(_ffmpeg_path)), 'bin', 'ffprobe')
        if os.path.isfile(_ffprobe_path):
            _ffprobe_path = os.path.realpath(_ffprobe_path)
        else:
            _ffprobe_path = None

datas = collect_data_files('yt_dlp')

binaries = []
if os.path.isfile(_ffmpeg_path):
    binaries.append((_ffmpeg_path, 'MacOS'))
if _ffprobe_path and os.path.isfile(_ffprobe_path):
    binaries.append((_ffprobe_path, 'MacOS'))

a = Analysis(
     ['youtube_downloader.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hidden_imports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='YouTube Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='YouTube Downloader.app',
    icon=None,
    bundle_identifier=None,
)
