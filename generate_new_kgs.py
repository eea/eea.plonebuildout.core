#!/usr/bin/env python

from distutils import version as vt
import os, sys
import re
import subprocess
import urllib


vfile_path = "https://svn.eionet.europa.eu/repositories/Zope/"\
             "trunk/www.eea.europa.eu/trunk/versions.cfg"
kgs_uri = "buildout-configs/kgs"


def _increment_version(version):
    """Given a tuple that contains a version number (1,0,1), returns
    a tuple with an incremented version (1,0,2)
    """

    last = True #flag for last digit, we treat it differently
    bump = False 
    out = []
    length = len(version)
    i = 0   
    for n in reversed(version):
        n = n + int(last) + int(bump)
        i += 1
        if n >= 10 and not (i == length):
            n = 0   
            bump = True
        else:   
            bump = False 
        last = False 
        out.append(n)

    return tuple(reversed(out))


def _get_latest_release(path):
    """Returns the highest version folder in path
    """
    folders = [vt.StrictVersion(f) for f in os.listdir(path) if f[0].isdigit()]
    folders.sort()
    if folders:
        return folders[-1]
    return None


def main():
    cwd = os.getcwd()

    #check that this is ran from a buildout folder
    if not 'buildout-configs' in os.listdir(cwd):
        print "Please run from the root of a "\
              "eea.plonebuildout.core git checkout"
        sys.exit(1)

    kgs_path = os.path.join(cwd, kgs_uri)
    latest = _get_latest_release(kgs_path)
    latest = latest.version[:2] #only want 2 numbers, ex: v 1.2

    next_ver = ".".join([str(x) for x in _increment_version(latest)])
    print "Creating kgs version", next_ver, '...',

    os.chdir(kgs_path)
    os.mkdir(next_ver)
    new_kgs = os.path.join(kgs_path, next_ver)
    with open(os.path.join(new_kgs, 'versions.cfg'), 'wb') as vfile:
        fp = urllib.urlopen(vfile_path)
        vfile.write(fp.read())

    #run zope_kgs_copy.py in buildout-configs/kgs/<x.x>/
    cmd = ['../zope_kgs_copy.py']

    try:
        subprocess.check_call(cmd, cwd=new_kgs, shell=True)
    except subprocess.CalledProcessError:
        print "error. \nGot an error while changing buildout files"
        sys.exit(1)

    # Update versions.cfg with the newly generated KGS version
    main_vfile_path = os.path.join(cwd, 'buildout-configs/versions.cfg')
    mvf = open(main_vfile_path)
    mvf_contents = mvf.read()
    mvf_contents = re.sub(r"(?<=kgs\/).*?(?=\/)", next_ver, mvf_contents)
    mvf.close()

    with open(main_vfile_path, 'wb') as mvf:
        mvf.write(mvf_contents)

    print "done"
    sys.exit(0)

if __name__ == "__main__":
    main()

