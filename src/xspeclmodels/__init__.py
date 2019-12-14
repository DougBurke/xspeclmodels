#
# This code is placed into the PUBLIC DOMAIN.
# It was written by Douglas Burke dburke.gw@gmail.com
#
"""
Sherpa interface to XSPEC local models:
    agnslim
    cluscool
    vcluscool
    zkerrbb

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

CpH     4   0.        1.e20           C_cph   add  0
peakT    keV     2.2       1.0e-1  1.0e-1   1.0e2       1.0e2       0.001
Abund    " "     1.       0.      0.       1000.       1000.       -0.01
Redshift " "     0.       1.0e-6  1.0e-6   50.         50.       -0.01
$switch    1

vCpH    17  0.         1.e20           C_vcph   add  0
peakT   keV     2.2       1.0e-1  1.0e-1   1.0e2       1.0e2       0.001
He       " "    1.    0.      0.   1000.     1000.       -0.01
C        " "    1.    0.      0.   1000.     1000.       -0.01
N        " "    1.    0.      0.   1000.     1000.       -0.01
O        " "    1.    0.      0.   1000.     1000.       -0.01
Ne       " "    1.    0.      0.   1000.     1000.       -0.01
Na       " "    1.    0.      0.   1000.     1000.       -0.01
Mg       " "    1.    0.      0.   1000.     1000.       -0.01
Al       " "    1.    0.      0.   1000.     1000.       -0.01
Si       " "    1.    0.      0.   1000.     1000.       -0.01
S        " "    1.    0.      0.   1000.     1000.       -0.01
Ar       " "    1.    0.      0.   1000.     1000.       -0.01
Ca       " "    1.    0.      0.   1000.     1000.       -0.01
Fe       " "    1.    0.      0.   1000.     1000.       -0.01
Ni       " "    1.    0.      0.   1000.     1000.       -0.01
Redshift " "    0.    1.0e-6  1.0e-6 50.       50.       -0.01
$switch    1

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


__all__ = ('XSagnslim', 'XSCph', 'XSvCph', 'XSzkerrbb', )


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


class XSCpH(XSAdditiveModel):
    """The XSPEC CpH model: Cluster cooling+heating

    See [1]_ for more information.

    Attributes
    ----------
    peakT
        The peak temperature, in keV
    Abund
        The abundance relative to solar
    Redshift
        The redshift of the gas
    switch
        0 for calculate, 1 for interpolate, 2 for AtomDB
    norm
        The mass-accretion rate, in solar masses/year.

    See Also
    --------
    XSvCph

    References
    ----------

    .. [1] https://github.com/HEASARC/xspec_localmodels/tree/master/cluscool

    """

    _calc = _models.C_cph

    def __init__(self, name='cph'):
        self.peakT = Parameter(name, 'peakT', 2.2, 0.1, 100, 0.1, 100,
                               units='keV')
        self.Abund = Parameter(name, 'Abund', 1, 0, 1000, 0, 1000,
                               frozen=True)
        self.Redshift = Parameter(name, 'Redshift', 1e-6, 1e-6, 50, 1e-6, 50,
                                  frozen=True)
        self.switch = Parameter(name, 'switch', 1, 0, 2, 0, 2,
                                alwaysfrozen=True)
        self.norm = Parameter(name, 'norm', 1.0, 0, 1e24, 0, hugeval)

        pars = (self.peakT, self.Abund, self.Redshift, self.switch, self.norm)
        XSAdditiveModel.__init__(self, name, pars)


class XSvCpH(XSAdditiveModel):
    """The XSPEC vCpH model: Cluster cooling+heating

    See [1]_ for more information.

    Attributes
    ----------
    peakT
        The peak temperature, in keV
    He
        He abundance relative to solar.
    C
        C abundance relative to solar.
    N
        N abundance relative to solar.
    O
        O abundance relative to solar.
    Ne
        Ne abundance relative to solar.
    Na
        Na abundance relative to solar.
    Mg
        Mg abundance relative to solar.
    Al
        Al abundance relative to solar.
    Si
        Si abundance relative to solar.
    S
        S abundance relative to solar.
    Ar
        Ar abundance relative to solar.
    Ca
        Ca abundance relative to solar.
    Fe
        Fe abundance relative to solar.
    Ni
        Ni abundance relative to solar.
    Redshift
        The redshift of the gas
    switch
        0 for calculate, 1 for interpolate, 2 for AtomDB
    norm
        The mass-accretion rate, in solar masses/year.

    See Also
    --------
    XSCph

    References
    ----------

    .. [1] https://github.com/HEASARC/xspec_localmodels/tree/master/cluscool

    """

    _calc = _models.C_vcph

    def __init__(self, name='vcph'):
        self.peakT = Parameter(name, 'peakT', 2.2, 0.1, 100, 0.1, 100,
                               units='keV')
        self.He = Parameter(name, 'He', 1, 0, 1000, 0, 1000, frozen=True)
        self.C = Parameter(name, 'C', 1, 0, 1000, 0, 1000, frozen=True)
        self.N = Parameter(name, 'N', 1, 0, 1000, 0, 1000, frozen=True)
        self.O = Parameter(name, 'O', 1, 0, 1000, 0, 1000, frozen=True)
        self.Ne = Parameter(name, 'Ne', 1, 0, 1000, 0, 1000, frozen=True)
        self.Na = Parameter(name, 'Na', 1, 0, 1000, 0, 1000, frozen=True)
        self.Mg = Parameter(name, 'Mg', 1, 0, 1000, 0, 1000, frozen=True)
        self.Al = Parameter(name, 'Al', 1, 0, 1000, 0, 1000, frozen=True)
        self.Si = Parameter(name, 'Si', 1, 0, 1000, 0, 1000, frozen=True)
        self.S = Parameter(name, 'S', 1, 0, 1000, 0, 1000, frozen=True)
        self.Ar = Parameter(name, 'Ar', 1, 0, 1000, 0, 1000, frozen=True)
        self.Ca = Parameter(name, 'Ca', 1, 0, 1000, 0, 1000, frozen=True)
        self.Fe = Parameter(name, 'Fe', 1, 0, 1000, 0, 1000, frozen=True)
        self.Ni = Parameter(name, 'Ni', 1, 0, 1000, 0, 1000, frozen=True)
        self.Redshift = Parameter(name, 'Redshift', 1e-6, 1e-6, 50, 1e-6, 50,
                                  frozen=True)
        self.switch = Parameter(name, 'switch', 1, 0, 2, 0, 2,
                                alwaysfrozen=True)
        self.norm = Parameter(name, 'norm', 1.0, 0, 1e24, 0, hugeval)

        pars = (self.peakT, self.He, self.C, self.N, self.O, self.Ne,
                self.Na, self.Mg, self.Al, self.Si, self.S, self.Ar,
                self.Ca, self.Fe, self.Ni,
                self.Redshift, self.switch, self.norm)
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
