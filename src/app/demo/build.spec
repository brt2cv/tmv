# -*- mode: python ; coding: utf-8 -*-
# pyinstaller.exe ../build_xxx.py -i "../app/xxx/res/yyy.ico" -p '../runtime/win32/python37/lib/;../runtime/win32/python37/libex/' -w

block_cipher = None

a = Analysis(['../../build.py'],
             pathex=[
                "../../../env/Lib/site-packages"],
             binaries=[],
             datas=[
                ("../../core/register/config", "core/register/config"),
                ("view/ui/*.py", "app/demo/view/ui"),
             ],
             hiddenimports=["app.demo.main"],
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
          name='Demo',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon='../mvtool/res/logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Demo')
