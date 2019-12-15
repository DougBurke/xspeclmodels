#
# This code is placed into the PUBLIC DOMAIN.
# It was written by Douglas Burke dburke.gw@gmail.com
#
"""
Sherpa interface to XSPEC local models from [1]_:

    agnslim
    zkerrbb
    thcompc (convolution; only supported if CIAO contrib package
             is loaded)

agnslim     14      0.03       1.e20          agnslim  add  0
mass        solar       1e7         1.0       1.0       1.e10   1.e10       -.1
dist        Mpc         100         0.01      0.01      1.e9    1.e9        -.01
logmdot     " "           1.      -10.      -10.        3       3           0.01
astar       " "           0.        0.        0.        0.998   0.998      -1
cosi        " "           0.5	    0.05      0.05	    1.	    1.         -1
kTe_hot     keV(-pl)    100.0      10        10       300      300         -1
kTe_warm    keV(-sc)      0.2       0.1       0.1       0.5      0.5        1e-2
Gamma_hot   " "           2.4       1.3       1.3       3        3.         0.01
Gamma_warm  "(-disk)"     3.0       2         2         5.      10.         0.01
R_hot       "Rg "        10.0       2.0       2.0     500      500          0.01
R_warm      "Rg"         20.0       2         2       500      500	        0.1
logrout     "(-selfg) "  -1.0      -3.0      -3.0       7.0      7.0       -1e-2
rin         ""           -1        -1        -1       100.     100.        -1
redshift    " "           0.0       0.        0.        5        5         -1

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

thcompc      3   0.03       1.e20           thcompf  con 0
gamma_tau   " "  1.7   1.001      1.001      5         10        0.01
kT_e        keV  50.   0.5        0.5      150.0      150.0      0.1
z           " "  0.0   0.0        0.0       5.0         5.0     -0.01

References
----------

.. [1] https://github.com/HEASARC/xspec_localmodels/

"""

from sherpa.models.parameter import Parameter, hugeval
from sherpa.astro.xspec import XSAdditiveModel, get_xsversion

try:
    from sherpa_contrib.xspec.xsmodels import XSConvolutionKernel
    support_convolve = True
except ImportError:
    support_convolve = False

from . import _models

__all__ = ['XSagnslim', 'XSzkerrbb']
if support_convolve:
    __all__.append('XSthcompc')

__all__ = tuple(__all__)


# We need to ensure that the XSPEC model library has been initialized
# before the model is evaluated. This could be handled in the
# Python<->C++ bridge, as it is with the XSPEC module that is
# distributed with CIAO, but here we just ensure that the library
# has been initialized when this module is imported.
#
get_xsversion()


class XSagnslim(XSAdditiveModel):
    """The XSPEC agnslim model: AGN super-Eddington accretion model

    See [1]_

    Attributes
    ----------
    mass
        black hole mass in solar masses
    dist
        comoving (proper) distance in Mpc
    logmdot
        mdot = Mdot / Mdot_edd where eta Mdot_Edd c^2 = L_Edd
    astar
        spin of the black hole (dimensionless)
    cosi
        cosine of the inclination angle i for the warm Comptonising component and
        the outer disc.
    kTe_hot
        electron temperature for the hot Comptonisation component in keV. If this
        parameter is negative then only the hot Comptonisation component is used.
    kTe_warm
        electron temperature for the warm Comptonisation component in keV. If this
        parameter is negative then only the warm Comptonisation component is used.
    Gamma_hot
        the spectral index of the hot Comptonisation component.
    Gamma_warm
        the spectral index of the warm Comptonisation component. If this parameter is
        negative then only the outer disc component is used.
    R_hot
        outer radius of the hot Comptonisation component in Rg
    R_warm
        outer radius of the warm Comptonisation component in Rg
    logrout
        log of the outer radius of the disc in units of Rg. If this parameter is negative,
        the code will use the self gravity radius as calculated from Laor & Netzer
        (1989, MNRAS, 238, 897L).
    rin
        the inner radius of the disc in Rg. If this parameter is -1 (the default), the
        model will use the radius calculated from KD19. This must be greater than R_hot
        for mdot greater than 6 and greater than R_isco for mdot less than 6.
    redshift
    norm
        this must be fixed to 1

    References
    ----------

    .. [1] https://github.com/HEASARC/xspec_localmodels/tree/master/agnslim

    """

    _calc = _models.agnslim

    def __init__(self, name='agnslim'):
        self.mass = Parameter(name, 'mass', 1e7, 1, 1e10, 1, 1e10,
                              units='solar', frozen=True)
        self.dist = Parameter(name, 'dist', 100, 0.01, 1e9, 0.01, 1e9,
                              units='Mpc', frozen=True)
        self.logmdot = Parameter(name, 'logmdot', 1, -10, 3, -10, 3)
        self.astar = Parameter(name, 'astar', 0, 0, 0.998, 0, 0.998,
                               frozen=True)
        self.cosi = Parameter(name, 'cosi', 0.5, 0.05, 1, 0.05, 1,
                              frozen=True)
        self.kTe_hot = Parameter(name, 'kTe_hot', 100, 10, 300, 10, 300,
                                 units='KeV(-pl)', frozen=True)
        self.kTe_warm = Parameter(name, 'kTe_warm', 0.2, 0.1, 0.5, 0.1, 0.5,
                                  units='KeV(-sc)')
        self.Gamma_hot = Parameter(name, 'Gamma_hot', 2.4, 1.3, 3, 1.3, 3)
        self.Gamma_warm = Parameter(name, 'Gamma_warm', 3.0, 2, 5, 2, 10,
                                    units='(-disk)')
        self.R_hot = Parameter(name, 'R_hot', 10, 2, 500, 2, 500,
                               units='Rg')
        self.R_warm = Parameter(name, 'R_warm', 20, 2, 500, 2, 500,
                               units='Rg')
        self.logrout = Parameter(name, 'logrout', -1.0, -3, 7, -3, 7,
                                 units='(-selfg)', frozen=True)
        self.rin = Parameter(name, 'rin', -1, -1, 100, -1, 100,
                             frozen=True)
        self.redshift = Parameter(name, 'redshift', 0, 0, 5, 0, 5,
                                  frozen=True)
        self.norm = Parameter(name, 'norm', 1.0, alwaysfrozen=True)

        pars = (self.mass, self.dist, self.logmdot, self.astar, self.cosi,
                self.kTe_hot, self.kTe_warm, self.Gamma_hot, self.Gamma_warm,
                self.R_hot, self.R_warm, self.logrout, self.rin,
                self.redshift, self.norm)
        XSAdditiveModel.__init__(self, name, pars)


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


if support_convolve:

    class XSthcompc(XSConvolutionKernel):
        """The XSPEC thcompc model: Thermally comptonized continuum

        For a description see [1]_.

        .. warning::
           This is a convolution kernel (that is, it modifies the spectrum
           created by a model expression). This means that it is used
           differently, and has seen *NO* testing. Note that Sherpa in
           CIAO 4.12 has no "easy" way to extend the analysis grid
           (although it can do so, this has not been tested with XSPEC
           models).

        Attributes
        ----------
        gamma_tau
            >0: the low-energy power-law photon index;
            <0: the Thomson optical depth (given by the absolute value).
        kT_e
            electron temperature (high energy rollover)
        z

        References
        ----------

        .. [1] https://github.com/HEASARC/xspec_localmodels/tree/master/thcompc

        Examples
        --------

        As this is a convolution model, it needs to be applied to a model
        expression, so we generate one using a powerlaw *just* for the example
        (in actual use this is likely to be more complex).

        >>> continuum = XSpowerlaw('continuum')
        >>> cmdl = XSthcompc('comptonization')
        >>> mdl = cmdl(continuum)

        """

        _calc = _models.thcompf

        def __init__(self, name='thcompc'):

            self.gamma_tau = Parameter(name, 'gamma_tau', 1.7, 1.001, 5,
                                       1.001, 10)
            self.kT_e = Parameter(name, 'kT_e', 50, 0.5, 150, 0.5, 150,
                                  units='keV')
            self.z = Parameter(name, 'z', 0.0, 0, 5, 0, 5,
                               frozen=True)

            pars = (self.gamma_tau, self.kT_e, self.z)
            XSConvolutionKernel.__init__(self, name, pars)
