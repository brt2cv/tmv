# -*- mode: python ; coding: utf-8 -*-
# pyinstaller.exe ../build_xxx.py -i "../app/xxx/res/yyy.ico" -p '../runtime/win32/python37/lib/;../runtime/win32/python37/libex/' -w

block_cipher = None

a = Analysis(['../build.py'],
             pathex=["../..",
                "../../runtime/win64/Lib/site-packages"],
             binaries=[],
             datas=[
                ("../../core/register/config", "core/register/config"),
                ("../../app/gui/res", "app/gui/res"),
                ("../../app/gui/view/ui", "app/gui/view/ui"),
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=["zmq"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Demo',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon='../ocrkit/res/ocr.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Demo')
