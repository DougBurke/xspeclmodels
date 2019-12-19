
# Allow the XSPEC local models to be used in Sherpa

This is an experiment in providing support for the
[XSPEC local models](https://github.com/HEASARC/xspec_localmodels)
in
[Sherpa](https://cxc.harvard.edu/sherpa/). It relies on you
having used the [conda installation
method](https://cxc.harvard.edu/ciao/download/conda.html) to
install CIAO 4.12.

At present the *only* supported models are:

 - `agnslim`
 - `thcompc` (although this is known to be problematic, so don't try it)
 - `zkerrbb`

and there has been *essentially no testing* to check this works
correctly (although development of this package did find
a bug in the FORTRAN code of the `zkerrbb` model).

At the moment I have only got this working with the conda
release of CIAO 4.12, using Linux/Python 3.7 and macOS/Python 3.7.
I have not tested the other conda Python versions, and it does
not seem to work with the ciao-install version of CIAO (this version
was build using an old version of gcc and it looks like it creates
a different ABI for the compiled code, and this is more than I ever
wanted to know about linkers so I am concentrating on the conda
version).

It *could* be made to work with CIAO 4.11 but I do not have time
to do so at this time, and CIAO 4.12 is now available. If you did
want to try, the include files in the `xspec/` directory
would have to be replaced with those for XSPEC 12.10.0, the
library versions for the XSPEC libraries changed in `setup.py`,
and the link issues mentioned above worked out (since CIAO 4.11
is only available via ciao-install).

## Models already in Sherpa

The following models are in XSPEC 12.10.1, and so are included in CIAO 4.12
(there will be no attempt to include these models in this module):

 - agnsed/: `agnsed`, `qsosed`
 - cluscool/: `cph`, `vcph`
 - ky/: `kyrline` (`kyconv` is a convolution model which is not directly-supported by Sherpa)

## What versions of the models are used?

The models are taken from the
[XSPEC GitHub repository](https://github.com/HEASARC/xspec_localmodels)
at the following revision:
[December 11 2019 - 5ef6af6ed9991746cbaef42c1fac3c054f6b955c](https://github.com/HEASARC/xspec_localmodels/blob/5ef6af6ed9991746cbaef42c1fac3c054f6b955c/README.md).

## Legal Terms

This code is released into the public domain, using the
[CC0 1.0 Universal (CC0 1.0) Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/), which can also be found in the
LICENSE file in the distribution.

## Author and Support

This was written by Doug Burke - dburke.gw@gmail.com - and
support is on a best-effort basis. It is *not* an official
product of my employer.

# Installation

Start up a conda-installed version of CIAO 4.12 and then try

```
% git clone https://github.com/DougBurke/xspeclmodels
% cd xspeclmodels
% python setup.py build_ext --inplace
```

Hopefully there'll be no error message here. Now try running the
tests (which may require you to `conda install pytest` first):

```
% pytest
=========================================== test session starts ============================================
platform linux -- Python 3.7.5, pytest-5.3.2, py-1.8.0, pluggy-0.13.1
rootdir: /somewhere/over/the/rainbow/xspeclmpodels
collected 15 items

src/tests/test_xspeclmodels.py ........                                                              [ 53%]
src/tests/test_xspeclmodels_ui.py .......                                                            [100%]

============================================= warnings summary =============================================
/home/ahappycamper/anaconda/envs/ciao412/lib/python3.7/site-packages/pytransform/__init__.py:13
  /home/ahappycamper/anaconda/envs/ciao412/lib/python3.7/site-packages/pytransform/__init__.py:13: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
    import imp

-- Docs: https://docs.pytest.org/en/latest/warnings.html
====================================== 15 passed, 1 warning in 1.85s =======================================
```

Note that the `DeprecationWarning` about `pytransform` can be ignored.
If there are any failures here then please check the
[issues list](https://github.com/DougBurke/xspeclmodels/issues) to see
if it's known about and, if not, add an issue.

Once the tests have passed (note that they are very limited, and are
only designed to check the models are "doing something", not that they
are doing the right thing!), you can install the module with:

```
% python setup.py install
```

# Use

After installation, you should be able to start Sherpa and
import the `xspeclmodels.ui` module, which will add the
XSPEC local models to Sherpa:

```
% sherpa
-----------------------------------------------------
Welcome to Sherpa: CXC's Modeling and Fitting Package
-----------------------------------------------------
Sherpa 4.12.0

Python 3.7.5 (default, Oct 25 2019, 15:51:11)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.10.2 -- An enhanced Interactive Python. Type '?' for help.

IPython profile: sherpa
Using matplotlib backend: Qt5Agg

sherpa In [1]: import xspeclmodels.ui
Adding XSPEC local model: xsagnslim
Adding XSPEC local model: xszkerrbb
Adding XSPEC local model: xsthcompc

sherpa In [2]: src = xsphabs.gal * xszkerrbb.mdl

sherpa In [3]: print(src)
(xsphabs.gal * xszkerrbb.mdl)
   Param        Type          Value          Min          Max      Units
   -----        ----          -----          ---          ---      -----
   gal.nH       thawed            1            0       100000 10^22 atoms / cm^2
   mdl.eta      frozen            0            0            1
   mdl.a        thawed          0.5        -0.99        0.999
   mdl.i        frozen           30            0           85     degree
   mdl.Mbh      frozen        1e+07            3        1e+10      M_sun
   mdl.Mdd      thawed            1        1e-05        10000       M0yr
   mdl.z        frozen         0.01            0           10
   mdl.fcol     frozen            2         -100          100
   mdl.rflag    thawed            1 -3.40282e+38  3.40282e+38
   mdl.lflag    thawed            1 -3.40282e+38  3.40282e+38
   mdl.norm     thawed            1            0        1e+24

sherpa In [4]: dataspace1d(0.1, 6, 0.01)

sherpa In [5]: set_source(src)

sherpa In [6]: plot_source(xlog=True, ylog=True)
```

![The absorbed model](imgs/example.png)

For those that just want the model class, and do not use the
Sherpa "UI" layer, you can just `import xspeclmodels`.

## I don't want screen output when I import the models!

The screen messages created by `xspeclmodels.ui` are from the
Sherpa logging instance, so you can turn them off when
importing the model with the following (don't forget to
change the `level` back to `INFO` afterwards!):

```
sherpa In [1]: import logging

sherpa In [2]: logger = logging.getLogger('sherpa')

sherpa In [3]: logger.setLevel(logging.WARNING)

sherpa In [4]: import xspeclmodels.ui

sherpa In [5]: logger.setLevel(logging.INFO)
```
