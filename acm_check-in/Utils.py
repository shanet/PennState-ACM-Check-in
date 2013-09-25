import os
import sys

def getAbsoluteResourcePath(relativePath):
    try:
        # PyInstaller stores data files in a tmp folder refered to as _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        # If not running as a PyInstaller created binary, try to find the data file as
        # an installed Python egg
        try:
            basePath = os.path.dirname(sys.modules[''].__file__)
        except Exception:
            basePath = ''

        # If the egg path does not exist, assume we're running as non-packaged
        if not os.path.exists(os.path.join(basePath, relativePath)):
            basePath = ''

    path = os.path.join(basePath, relativePath)

    # If the path still doesn't exist, this function won't help you
    if not os.path.exists(path):
        return None

    return path
