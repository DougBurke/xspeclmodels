"""
Test the object API to xspeclmodels. There is limited testing done here.

Some of this is essentially copying what is in __init__.py, but did
actually find something I'd forgotten to implement...
"""

import pytest

import numpy as np
from sherpa.astro.xspec import XSAdditiveModel, XSphabs, XSgaussian

try:
    from sherpa_contrib.xspec.xsmodels import XSConvolutionKernel
    support_convolve = True
except ImportError:
    support_convolve = False


EXPECTED_MODELS = set(['XSagnslim', 'XSzkerrbb'])
if support_convolve:
    EXPECTED_MODELS.add('XSthcompc')


def test_can_we_import():

    import xspeclmodels


def test_do_we_import_all_the_things():

    import xspeclmodels
    syms = set(xspeclmodels.__all__)
    assert syms == EXPECTED_MODELS


def test_create_agnslim():
    """Can we create an agnslim instance?"""

    from xspeclmodels import XSagnslim
    mdl = XSagnslim('foo')
    assert isinstance(mdl, XSAdditiveModel)
    assert mdl.type == 'xsagnslim'
    assert mdl.name == 'foo'
    assert len(mdl.pars) == 15
    assert mdl.pars[0].name == 'mass'
    assert mdl.pars[1].units == 'Mpc'
    assert mdl.pars[3].frozen
    assert mdl.pars[4].val == pytest.approx(0.5)
    assert mdl.pars[14].name == 'norm'


def test_create_zkerrbb():
    """Can we create a zkerrbb instance?"""

    from xspeclmodels import XSzkerrbb
    mdl = XSzkerrbb('zb')
    assert isinstance(mdl, XSAdditiveModel)
    assert mdl.type == 'xszkerrbb'
    assert mdl.name == 'zb'
    assert len(mdl.pars) == 10
    assert mdl.pars[0].name == 'eta'
    assert mdl.pars[2].units == 'degree'
    assert mdl.pars[3].frozen
    assert mdl.pars[5].val == pytest.approx(0.01)
    assert mdl.pars[8].alwaysfrozen
    assert mdl.pars[9].name == 'norm'


@pytest.mark.skipif(not support_convolve,
                    reason='ciao-contrib module not installed')
def test_create_thcompc():
    """Can we create a thcompc instance?"""

    from xspeclmodels import XSthcompc
    mdl = XSthcompc('conv')
    assert isinstance(mdl, XSConvolutionKernel)
    assert mdl.type == 'xsthcompc'
    assert mdl.name == 'conv'
    assert len(mdl.pars) == 3
    assert mdl.pars[0].name == 'gamma_tau'
    assert mdl.pars[1].units == 'keV'
    assert mdl.pars[1].val == pytest.approx(50)


def test_can_evaluate_agnslim():
    """Does this create some emission?

    It does not test the result is actualy meaningful.
    """

    from xspeclmodels import XSagnslim
    m1 = XSagnslim('m1')
    m2 = XSphabs('m2')

    # test out a combined model; not really needed but this is
    # closer to how people will be using it.
    #
    src = m2 * m1

    egrid = np.arange(0.1, 10, 0.01)
    elo = egrid[:-1]
    ehi = egrid[1:]

    y1 = src(egrid)
    y2 = src(elo, ehi)

    # Assume there is some emission
    assert (y1 > 0).any()
    assert (y1[:-1] == y2).all()


def test_can_evaluate_zkerrbb():
    """Does this create some emission?

    It does not test the result is actualy meaningful.
    """

    from xspeclmodels import XSzkerrbb
    m1 = XSzkerrbb('m1')
    m2 = XSphabs('m2')

    # test out a combined model; not really needed but this is
    # closer to how people will be using it.
    #
    src = m2 * m1

    egrid = np.arange(0.1, 10, 0.01)
    elo = egrid[:-1]
    ehi = egrid[1:]

    y1 = src(egrid)
    y2 = src(elo, ehi)

    # Assume there is some emission
    assert (y1 > 0).any()
    assert (y1[:-1] == y2).all()


@pytest.mark.skipif(not support_convolve,
                    reason='ciao-contrib module not installed')
def test_can_evaluate_thcompc():
    """Does this redistribute some emission?

    It does not test the result is actualy meaningful, but
    does check it's done something
    """

    from xspeclmodels import XSthcompc
    m1 = XSgaussian('m1')
    m1.lineE = 5.0
    m1.Sigma = 1.0

    mconv = XSthcompc('mconv')

    # The line (m1) should be redistributed by the convolution
    # component.
    mdl = mconv(m1)

    egrid = np.arange(0.1, 10, 0.01)
    elo = egrid[:-1]
    ehi = egrid[1:]

    y1 = m1(egrid)
    y1conv = mdl(egrid)

    y2 = m1(elo, ehi)
    y2conv = mdl(elo, ehi)

    # Assume there is some emission
    # We test the line-only model as well just as a check
    assert (y1 > 0).any()
    assert (y1conv > 0).any()

    assert (y1[:-1] == y2).all()
    assert (y1conv[:-1] == y2conv).all()

    # not guaranteed the peak will be reduced (depends on what
    # the convolution is doing), and I would hope that flux
    # is at best conserved (ie not created), and that we don't
    # have to worry about numerical artifacts here.
    #
    assert y2.max() > y2conv.max()
    assert y2.sum() >= y2conv.sum()
