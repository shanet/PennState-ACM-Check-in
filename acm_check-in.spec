# -*- mode: python -*-
import sys

a = Analysis(['acm_check-in/Check-in.py'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          # Static link the Visual C++ Redistributable DLLs if on Windows
          a.binaries + [('msvcp100.dll', 'C:\\Windows\\System32\\msvcp100.dll', 'BINARY'),
                        ('msvcr100.dll', 'C:\\Windows\\System32\\msvcr100.dll', 'BINARY')]
          if sys.platform == 'win32' else a.binaries,
          a.zipfiles,
          a.datas + [('images/green_check_mark.png',  'acm_check-in/images/green_check_mark.png', 'DATA'),
                     ('images/loading_icon.gif',      'acm_check-in/images/loading_icon.gif',     'DATA'),
                     ('images/login_logo.png',        'acm_check-in/images/login_logo.png',       'DATA'),
                     ('images/magnetic_card.png',     'acm_check-in/images/magnetic_card.png',    'DATA'),
                     ('images/main_logo.png',         'acm_check-in/images/main_logo.png',        'DATA'),
                     ('images/red_x_mark.png',        'acm_check-in/images/red_x_mark.png',       'DATA'),
                     ('images/trophy.png',            'acm_check-in/images/trophy.png',           'DATA')],
          name=os.path.join('dist', 'ACM-Check-in' + ('.exe' if sys.platform == 'win32' else '')),
          debug=False,
          strip=None,
          upx=True,
          console=False)

# Build a .app if on OS X
if sys.platform == 'darwin':
   app = BUNDLE(exe,
                name='ACM-Check-in.app',
                icon=None)
