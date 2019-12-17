# -*- mode: python ; coding: utf-8 -*-
# pyinstaller.exe ../build_xxx.py -i "../app/xxx/res/yyy.ico" -p '../runtime/win32/python37/lib/;../runtime/win32/python37/libex/' -w

block_cipher = None

a = Analysis(['../build_triage.py'],
             pathex=['../runtime/win64/Lib/site-packages'],
             binaries=[],
             datas=[
                ("../core/viewer/config", "core/viewer/config"),
                ("../core/viewer/res", "core/viewer/res"),
                ("../core/viewer/view/ui", "core/viewer/view/ui"),
                ("../app/mvtool/res", "app/mvtool/res"),
                ("../app/mvtool/view/ui", "app/mvtool/view/ui"),
             ],
             hiddenimports=["app.mvtool.main"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
          name='Triage',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='../app/ocrkit/res/ocr.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Triage')
