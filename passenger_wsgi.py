import sys, os

INTERP = "/var/www/html/lmgapp/bin/python"

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append('lmgapp')
    
from run import app as application