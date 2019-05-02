# -*- mode: python -*-

block_cipher = None

def recurse_for_py_files(names_so_far):
  returnvalue = []
  for name in os.listdir(os.path.join(*names_so_far)):
    if name != "__pycache__":
      subdir_name = os.path.join(*names_so_far, name)
      if os.path.isdir(subdir_name):
        new_name_list = names_so_far + [name]
        for filename in os.listdir(os.path.join(*new_name_list)):
          base_file,file_extension = os.path.splitext(filename)
          if file_extension == ".py":
            returnvalue.append(".".join(new_name_list + [base_file]))
        returnvalue.extend(recurse_for_py_files(new_name_list))
  return returnvalue

hiddenimports = recurse_for_py_files(["source"])

a = Analysis(['SpriteSomething.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=hiddenimports,
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SpriteSomething',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )   #   <--- change this to True to enable command prompt when the app runs
