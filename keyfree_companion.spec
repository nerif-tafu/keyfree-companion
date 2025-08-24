# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('bunny.png', '.')],
    hiddenimports=[
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'pynput.keyboard._util_win32',
        'pynput.mouse._util_win32',
        'flask',
        'flask_cors',
        'requests',
        'pyperclip',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'json',
        'threading',
        'time',
        'queue',
        'keyboard_simulator',
        'server',
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KeyFreeCompanion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
         console=False,  # Set to True if you want a console window
     disable_windowed_traceback=False,
     argv_emulation=False,
     target_arch=None,
     codesign_identity=None,
     entitlements_file=None,
     icon=os.path.abspath('bunny_new.ico'),  # Use absolute path to bunny_new.ico as the executable icon
     version='file_version_info.txt',
)
