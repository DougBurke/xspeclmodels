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
# in the object file. I have tried to integrate this into the
# "command" system of the build process, but perhaps I should just
# treat the FORTRAN code as creating a separate library that needs
# to be compiled as part of the build?
#

import os

import setuptools

# from numpy.distutils.core import setup, Extension
from distutils.core import Extension
from distutils.command.build_ext import build_ext

from distutils import log

import numpy
from numpy.distutils import fcompiler

import sherpa

def up(p):
    return os.path.dirname(p)

# What is the best way to find the Sherpa-provided include files?
# I was trying to support both ciao-install and conda installations
# of CIAO, but I have "given up" on ciao-install for now.
#
# Should Sherpa provide a way to get at this path?
#
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
FORTRANFILES = ['src/xspec/agnslim.f',
                'src/xspec/zrunkbb.f',
                'src/xspec/th.f90']


# Seems to be needed on macOS, otherwise link time creates this
# message:
#
# ld: warning: could not create compact unwind for _zrunkbb_: stack subq instruction is too different from dwarf stack size
#
# No idea if this breaks anything (more likely to slow the execution of
# the code, from what the internet tells me).
#
if os.uname().sysname == 'Darwin':
    cargs = ['-Wl,-no_compact_unwind']
else:
    cargs = []

mod = Extension('xspeclmodels._models',
                include_dirs=includes,
                library_dirs=libs,
                libraries=libnames,
                sources=['src/xspeclmodels/src/_models.cxx',
                         'src/xspec/zkerrbb.cxx'],
                extra_link_args=cargs,
                # extra_link_args=['-lgfortran'],
                depends=FORTRANFILES
                )

# TODO:
#
# This could be made more generic by inspecting the sources sent
# in to it, and pulling out the FORTRAN code from it. It also always
# recompiles the FORTRAN code, even if it hasn't changed, but then
# doesn't do anything with it.
#
# Should I really be looking at build_clib for inspiration, guidance,
# and fashion tips?
#
class ExtBuild(build_ext):

    def run(self):

        # Manually compile the FORTRAN code; this is all a bit too
        # hand coded
        #
        cmplr = fcompiler.new_fcompiler()
        cmplr.customize()

        self.announce('Compiling FORTRAN code', level=log.INFO)
        fobjs = cmplr.compile(FORTRANFILES,
                              output_dir=self.build_temp,
                              debug=self.debug)

        # Could just append if set, but for now expect not to be
        # set, so error out if this changes
        #
        assert self.link_objects is None, \
            'unexpected: link_objects={}'.format(self.link_objects)
        self.link_objects = fobjs

        super().run()


kwargs = {
    'name': 'xspeclmodels',
    'author': 'Douglas Burke',
    'author_email': 'dburke.gw@gmail.com',
    'version': '1.0',
    'description': 'XSPEC user-models in Sherpa: agnslim, zkerrbb, thcompc',
    'long_description': open('README.md', 'rt').read(),
    'long_description_content_type': 'text/markdown',

    'packages': setuptools.find_packages('src'),
    'package_dir': {'': 'src/'},

    'ext_modules': [mod],

    'classifiers': [
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedicationm',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'Development Status :: 3 - Alpha'
    ],

    'cmdclass': { 'build_ext': ExtBuild },
}

setuptools.setup(**kwargs)
