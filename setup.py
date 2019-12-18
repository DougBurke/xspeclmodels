#
# A rather hacky way to build the XSPEC local model code,
# which is a collection of C++ and FORTRAN, and take advantage
# of the interface that the Sherpa XSPEC model uses (that handles
# the conversion from the user-supplied grid to the one that
# XSPEC needs).
#
# It is also complicated by the need to access the XSPEC model
# include files, which in the HEASARC environment requires
# access to the build directory. As we don't have this in an
# installed version of the XSPEC model library (the header
# files seem to get installed but all in the same directory,
# which means that paths like XSFunctions/Utilities/FunctionUtulity.h
# can't be resolved), I have just included the full set of headers
# from XSPEC 12.10.1 - patch level m I think - in this repository.
# Hopefully there aren't any significant changes in these over time ;-)
# There is also the fact that the XSPEC library requires linking to
# a set of versioned libraries, so this is also version dependent.
#
# A large complication is that I want to compile FORTRAN code and
# link it into the extension, but do not want any Python interface
# to this code. My experiments to stop f2py from creating such an
# interface have been fruitless so far. So this module manually
# compiles the FORTRAN code and then tells the Extension to link
# in the object file.
#

import os
import subprocess

# from numpy.distutils.core import setup, Extension
from distutils.core import setup, Extension

import numpy
from numpy.distutils import fcompiler

import sherpa

def up(p):
    return os.path.dirname(p)

# What is the best way to find the Sherpa-provided include files?
basepath = up(sherpa.__file__)
sherpa_incpath = os.path.join(basepath, 'include')
xspec_basedir = "xspec"
includes = [numpy.get_include(), sherpa_incpath]
for dname in ["", "include", "XSFunctions"]:
    includes.append(os.path.join(xspec_basedir, dname))

for include in includes:
    if not os.path.isdir(include):
        raise IOError("Unable to find {}".format(include))

# Where are the XSPEC libraries?
#
# They are located in different places in ciao-install vs conda,
# but for now concentrating on conda and - on Linux at least -
# the path doesn't appear to be needed
#
libs = []

# the choice of libs depends on the XSPEC model library version,
# which makes this harder to write than I'd like. So Let's just
# hard code it at the moment.
#
libnames = ["XSFunctions", "XSUtil", "XS", "hdsp_6.26",
            "CCfits_2.5", "cfitsio"]

# What FORTRAN code needs compiling?
#
fdir = os.path.join('src', 'xspeclmodels', 'src')
f77 = []
f90 = []
for fhead in ['agnslim', 'zrunkbb']:
    fcode = os.path.join(fdir, '{}.f'.format(fhead))

    # Would realy like to put this in the build directory
    #
    fobj = os.path.join(fdir, '{}.o'.format(fhead))

    f77.append((fcode, fobj))

for fhead in ['th']:
    fcode = os.path.join(fdir, '{}.f90'.format(fhead))

    # Would realy like to put this in the build directory
    #
    fobj = os.path.join(fdir, '{}.o'.format(fhead))

    f90.append((fcode, fobj))

fobjs = [o for _,o in f77] + [o for _,o in f90]

mod = Extension('xspeclmodels._models',
                include_dirs=includes,
                library_dirs=libs,
                libraries=libnames,
                sources=['src/xspeclmodels/src/_models.cxx',
                         'src/xspeclmodels/src/zkerrbb.cxx'],
                extra_objects=fobjs,
                extra_link_args=['-Wl,-no_compact_unwind'],
                # extra_link_args=['-lgfortran'],
                depends=fobjs,
                )

# Manually compile the FORTRAN code; really should place this into the
# build directory but for now just do it here. It's also not clear to
# me if this is the most-sensible way to do this (I would be surprised
# as it is the first-ish thing I got to work).
#
cmplr = fcompiler.new_fcompiler()
cmplr.customize()

for fcode, fobj in f77:
    if os.path.exists(fobj):
        os.remove(fobj)

    cmds = cmplr.compiler_f77 + ['-c', fcode, '-o', fobj]
    print("Manually building FORTRAN 77 with:")
    print(" ".join(cmds))
    subprocess.run(cmds, check=True)

    if not os.path.exists(fobj):
        raise IOError("Unable to compile {} to create {}".format(fcode, fobj))

for fcode, fobj in f90:
    if os.path.exists(fobj):
        os.remove(fobj)

    cmds = cmplr.compiler_f90 + ['-c', fcode, '-o', fobj]
    print("Manually building FORTRAN 90 with:")
    print(" ".join(cmds))
    subprocess.run(cmds, check=True)

    if not os.path.exists(fobj):
        raise IOError("Unable to compile {} to create {}".format(fcode, fobj))


setup(name='xspeclmodels',
      author='Douglas Burke',
      author_email='dburke.gw@gmail.com',
      version='1.0',
      description='XSPEC user-models in Sherpa: zkerrbb',
      long_description=open('README.md', 'rt').read(),
      long_description_content_type='text/markdown',
      packages=['xspeclmodels'],
      package_dir={'xspeclmodels': 'src/xspeclmodels',
                   'xspeclmodels._models': 'src/xspeclmodels/src'},
      ext_modules=[mod],
      classifiers=['License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedicationm',
                   'Intended Audience :: Science/Research',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: Implementation :: CPython',
                   'Topic :: Scientific/Engineering :: Astronomy',
                   'Topic :: Scientific/Engineering :: Physics',
                   'Development Status :: 3 - Alpha'
          ]
)
