#!C:\Users\Alexey\Documents\GitHub\Kochev_Yusupov_JKH\JKH\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'pyramid==1.5b1','console_scripts','pserve'
__requires__ = 'pyramid==1.5b1'
import sys
from pkg_resources import load_entry_point

sys.exit(
   load_entry_point('pyramid==1.5b1', 'console_scripts', 'pserve')()
)
