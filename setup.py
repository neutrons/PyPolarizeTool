import codecs
import sys
import os
import re
import versioneer  # https://github.com/warner/python-versioneer

from setuptools import setup, find_packages

if sys.argv[-1] == 'pyuic':
    # convert the UI in designer (for the application)
    indir = 'designer'
    outdir = 'py4circle/interface/gui'
    files = os.listdir(indir)
    files = [os.path.join('designer', item) for item in files]
    files = [item for item in files if item.endswith('.ui')]

    try:
        import PyQt5
        pyui_ver = 5
    except ImportError:
        pyui_ver = 4
    
    done = 0
    for inname in files:
        base_inname = os.path.basename(inname)
        outname = 'ui_' + base_inname.replace('.ui', '.py')
        outname = os.path.join(outdir, outname)
        if os.path.exists(outname):
            if os.stat(inname).st_mtime < os.stat(outname).st_mtime:
                continue
        print("Converting '%s' to '%s'" % (inname, outname))

        try:
            # check the key package to determine whether the build shall be Qt4 or Qt5
            import PyQt5
            from qtconsole.inprocess import QtInProcessKernelManager
            ver = 5
            print ('Qt5 is used!')
        except ImportError:
            ver = 4
            print ('Qt4 is used!')

        command = "pyuic%d %s -o %s" % (ver, inname, outname)
        os.system(command)
        done += 1

    if not done:
        print("Did not convert any '.ui' files")

    # convert the UI in test/widgettest (for the application)
    # indir = 'tests/widgets'
    # outdir = 'py4circle/interface/gui'  # all UI shall be in the same directory with widgets module to avoid importing issue
    # files = os.listdir(indir)
    # files = [os.path.join(indir, item) for item in files]
    # files = [item for item in files if item.endswith('.ui')]

    # done = 0
    # for inname in files:
    #     base_inname = os.path.basename(inname)
    #     outname = 'uitest_' + base_inname.replace('.ui', '.py')
    #     outname = os.path.join(outdir, outname)
    #     if os.path.exists(outname):
    #         if os.stat(inname).st_mtime < os.stat(outname).st_mtime:
    #             continue
    #     print("Converting '%s' to '%s'" % (inname, outname))
    #     command = "pyuic%d %s -o %s"  % (pyui_ver, inname, outname)
    #     os.system(command)
    #     done += 1
    # if not done:
    #     print("Did not convert any '.ui' files")
    sys.exit(0)

###################################################################

NAME = "py4circle"
PACKAGES = find_packages(where="src")
PACKAGES = ["py4circle", "py4circle/lib", "py4circle/interface", "py4circle/interface/gui"]
META_PATH = os.path.join("src", "py4circle", "__init__.py")
KEYWORDS = ["class", "attribute", "boilerplate"]
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
INSTALL_REQUIRES = []

###################################################################

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    # print (r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta))
    # print (META_FILE)
    # print (re.M)
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


if __name__ == "__main__":
    """
    main
    """
    scripts = ['scripts/four']
    test_scripts = [ ]
    scripts.extend(test_scripts)

    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("url"),
        version=find_meta("version"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("email"),
        keywords=KEYWORDS,
        long_description=read("README.rst"),
        packages=PACKAGES,
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        # from ours
        package_dir={},  # {"": "src"},
        scripts=scripts,
        cmdclass=versioneer.get_cmdclass(),
    )

    print ('Scripts compiled: {0}'.format(scripts))
