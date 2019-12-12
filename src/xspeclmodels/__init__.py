#
# This code is placed into the PUBLIC DOMAIN.
# It was written by Douglas Burke dburke.gw@gmail.com
#
"""
Sherpa interface to the XSPEC local model: zkerrbb

% cat lmodel.dat
zkerrbb  9     0.     1.e6      C_zkerrbb  add     0
eta   " "        0.     0.     0.        1.0          1.0       -0.01
a     " "        0.5 -0.99   -0.99     0.9999       0.9999        0.01
i     degree     30.    0.     0.       85.          85.        -0.01
Mbh   M_sun      1e7    3.     3.      1e10         1e10         -1e5
Mdd   M0yr       1.   1e-5    1e-4    1e4          1e5         0.01
z     " "        0.01  0.     0.      10.           10.         -0.001
fcol  " "        2.  -100.  -100.      100.         100.        -0.01
$rflag     1
$lflag     1

"""

from sherpa.models.parameter import Parameter, hugeval
from sherpa.astro.xspec import XSAdditiveModel, get_xsversion

from . import _models


__all__ = ('XSzkerrbb', )


# We need to ensure that the XSPEC model library has been initialized
# before the model is evaluated. This could be handled in the
# Python<->C++ bridge, as it is with the XSPEC module that is
# distributed with CIAO, but here we just ensure that the library
# has been initialized when this module is imported.
#
get_xsversion()


class XSzkerrbb(XSAdditiveModel):
    """The XSPEC zkerrbb model

    Description is taken from XSkerrbb; it is assumed this is
    correct.

    Attributes
    ----------
    eta
        The ratio of the disk power produced by a torque at the disk
        inner boundary to the disk power arising from accretion.
    a
        The specific angular momentum of the black hole in units of the
        black hole mass M (when G=c=1). It should be in the range [0, 1).
    i
        The disk inclination angle, in degrees. A face-on disk has
        i=0. It must be less than or equal to 85 degrees.
    Mbh
        The mass of the black hole, in solar masses.
    Mdd
        The "effective" mass accretion rate in units of 10^18 g/s.
    z
        The distance to the black hole, as a redshift.
    fcol
        Possibly the spectral hardening factor.
    rflag
        A flag to switch on or off the effect of self irradiation:
        when greater than zero the self irradition is included,
        otherwise it is not. This parameter can not be thawed.
    lflag
        A flag to switch on or off the effect of limb darkening:
        when greater than zero the disk emission is assumed to be
        limb darkened, otherwise it is isotropic.
        This parameter can not be thawed.
    norm
        The normalization of the model. It should be fixed to 1
        if the inclination, mass, and distance are frozen.

    See Also
    --------
    XSkerrbb

    """

    _calc = _models.C_zkerrbb

    def __init__(self, name='zkerrbb'):
        self.eta = Parameter(name, 'eta', 0, 0, 1.0, 0, 1.0,
                             frozen=True)
        self.a = Parameter(name, 'a', 0.5, -0.99, 0.999, -0.99, 0.9999)
        self.i = Parameter(name, 'i', 30, 0, 85, 0, 85,
                           units='degree', frozen=True)
        self.Mbh = Parameter(name, 'Mbh', 1e7, 3, 1e10, 3, 1e10,
                             units='M_sun', frozen=True)
        self.Mdd = Parameter(name, 'Mdd', 1, 1e-5, 1e4, 1e-5, 1e5,
                             units='M0yr')
        self.z = Parameter(name, 'z', 0.01, 0, 10, 0, 10, frozen=True)
        self.fcol = Parameter(name, 'fcol', 2, -100, 100, -100, 100,
                              frozen=True)
        self.rflag = Parameter(name, 'rflag', 1)
        self.lflag = Parameter(name, 'lflag', 1)
        self.norm = Parameter(name, 'norm', 1.0, 0, 1e24, 0, hugeval)

        pars = (self.eta, self.a, self.i, self.Mbh, self.Mdd, self.z,
                self.fcol, self.rflag, self.lflag, self.norm)
        XSAdditiveModel.__init__(self, name, pars)
