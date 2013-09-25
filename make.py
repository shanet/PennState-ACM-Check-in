#! /usr/bin/env python

import os
import shutil
import subprocess
import sys

def clean():
    deleteDirectory('build')
    deleteDirectory('dist')
    deleteFile('logdict2.7.3.final.0-1.log')


def deleteDirectory(path):
    try:
        shutil.rmtree(path)
    except OSError as ose:
        # Ignore 'no such file or directory' errors
        if ose.errno != 2:
            print ose


def deleteFile(path):
    try:
        os.unlink(path)
    except OSError as ose:
        if ose.errno != 2:
            print ose


arg = sys.argv[1] if len(sys.argv) >= 2 else None

if arg == 'dist':
    if len(sys.argv) == 3:
        pyinstallerPath = sys.argv[2]
    else:
        pyinstallerPath = raw_input("Path to pyinstaller: ")
    clean()
    subprocess.call(['python', os.path.join(pyinstallerPath, 'pyinstaller.py'), 'acm_check-in.spec'])

elif arg == 'run':
    subprocess.call(['python', os.path.join('acm_check-in', 'Check-in.py')])

elif arg == 'clean':
    clean()

else:
    print "Invalid option\nPossible options: dist, run, clean"
