"""
Test the Session/UI interface to xspeclmodels: limited testing.

"""

import pytest

import numpy as np

from sherpa.astro import ui
from sherpa.astro.xspec import XSAdditiveModel

try:
    from sherpa_contrib.xspec.xsmodels import XSConvolutionKernel
    support_convolve = True
except ImportError:
    support_convolve = False

# Given how xspeclmodels.ui works - in that it registers models
# into the ui namespace, there isn't much point in importing
# it in every test, as is done in test_xspeclmodels.py
#
try:
    import xspeclmodels.ui
    imported = True
except ImportError:
    imported = False

skip = pytest.mark.skipif(not imported, reason='unable to import module')

EXPECTED_MODELS = set(['xsagnslim', 'xszkerrbb'])
if support_convolve:
    EXPECTED_MODELS.add('xsthcompc')

def test_can_we_import():

    assert imported


@skip
def test_do_we_import_all_the_things():

    xsmodels = ui.list_models('xs')
    for sym in EXPECTED_MODELS:
        assert sym in xsmodels


@skip
def test_create_agnslim():
    """Can we create an agnslim instance?"""

    ui.clean()

    # Why do I have to use create_model_component? Is it because
    # we have only registered xsagnslim into the global namespace
    # and not ui?
    #
    # mdl = ui.xsagnslim.foo
    #
    mdl = ui.create_model_component('xsagnslim', 'foo')
    assert isinstance(mdl, XSAdditiveModel)
    assert mdl.type == 'xsagnslim'
    assert mdl.name == 'xsagnslim.foo'
    assert len(mdl.pars) == 15
    assert mdl.pars[0].name == 'mass'
    assert mdl.pars[1].units == 'Mpc'
    assert mdl.pars[3].frozen
    assert mdl.pars[4].val == pytest.approx(0.5)
    assert mdl.pars[14].name == 'norm'


@skip
def test_create_zkerrbb():
    """Can we create a zkerrbb instance?"""

    ui.clean()

    # mdl = ui.xszkerrbb.zb
    mdl = ui.create_model_component('xszkerrbb', 'zb')

    assert isinstance(mdl, XSAdditiveModel)
    assert mdl.type == 'xszkerrbb'
    assert mdl.name == 'xszkerrbb.zb'
    assert len(mdl.pars) == 10
    assert mdl.pars[0].name == 'eta'
    assert mdl.pars[2].units == 'degree'
    assert mdl.pars[3].frozen
    assert mdl.pars[5].val == pytest.approx(0.01)
    assert mdl.pars[8].alwaysfrozen
    assert mdl.pars[9].name == 'norm'


@skip
@pytest.mark.skipif(not support_convolve,
                    reason='ciao-contrib module not installed')
def test_create_thcompc():
    """Can we create a thcompc instance?"""

    ui.clean()

    # mdl = ui.xsthcompc.conv
    mdl = ui.create_model_component('xsthcompc', 'conv')
    assert isinstance(mdl, XSConvolutionKernel)
    assert mdl.type == 'xsthcompc'
    assert mdl.name == 'xsthcompc.conv'
    assert len(mdl.pars) == 3
    assert mdl.pars[0].name == 'gamma_tau'
    assert mdl.pars[1].units == 'keV'
    assert mdl.pars[1].val == pytest.approx(50)


@skip
@pytest.mark.parametrize('mname', ['xsagnslim', 'xszkerrbb'])
def test_can_evaluate_additive_models(mname):
    """Does this create some emission?

    It does not test the result is actualy meaningful,
    and relies on the slightly-more-involved tests in
    test_xspeclmodels.py for the model evaluation.
    """

    ui.clean()
    m1 = ui.create_model_component(mname, 'm1')

    # test out a combined model; not really needed but this is
    # closer to how people will be using it.
    #
    ui.dataspace1d(0.1, 10, 0.01)
    ui.set_source(ui.xsphabs.m2 * m1)

    # rely on test_xspeclmodels.py for a more-complete test of
    # the model calling
    y = ui.get_model_plot().y.copy()

    # Assume there is some emission
    assert (y > 0).any()



# This test is known to cause a core dump. So let's not run it for now.
@skip
@pytest.mark.skipif(not support_convolve,
                    reason='ciao-contrib module not installed')
def _test_can_evaluate_thcompc():
    """Does this redistribute some emission?

    It does not test the result is actualy meaningful, but
    does check it's done something
    """

    ui.clean()

    ui.dataspace1d(0.1, 10, 0.01, id='unconv')
    ui.dataspace1d(0.1, 10, 0.01, id='conv')

    mconv = ui.create_model_component('xsthcompc', 'conv')
    ui.set_source('conv', mconv(ui.xsgaussian.m1))

    m1 = ui.get_model_component('m1')
    ui.set_source('unconv', m1)
    m1.lineE = 5.0
    m1.Sigma = 1.0

    yunconv = ui.get_model_plot('unconv').y.copy()
    yconv = ui.get_model_plot('conv').y.copy()

    assert (yunconv > 0).any()
    assert (yconv > 0).any()

    # not guaranteed the peak will be reduced (depends on what
    # the convolution is doing), and I would hope that flux
    # is at best conserved (ie not created), and that we don't
    # have to worry about numerical artifacts here.
    #
    assert yunconv.max() > yconv.max()
    assert yunconv.sum() >= yconv.sum()
