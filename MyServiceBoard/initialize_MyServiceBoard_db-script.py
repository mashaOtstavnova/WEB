#!c:\env\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'MyServiceBoard==0.0','console_scripts','initialize_MyServiceBoard_db'
__requires__ = 'MyServiceBoard==0.0'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('MyServiceBoard==0.0', 'console_scripts', 'initialize_MyServiceBoard_db')()
    )
