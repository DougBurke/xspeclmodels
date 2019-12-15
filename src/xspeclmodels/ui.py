#
# This code is placed into the PUBLIC DOMAIN.
# It was written by Douglas Burke dburke.gw@gmail.com
#
"""
Provide access to the local models when using the Sherpa UI
layer.

The added models are reported to the user using Sherpa's logger
at the logging.INFO level. If the model exists in Sherpa's XSPEC
module then we skip it here.

"""

import logging

from sherpa.astro import ui
from sherpa.astro import xspec

import xspeclmodels

logger = logging.getLogger('sherpa')

# For now process all models (including convolution style) the
# same way.
#
xsmodels = set([n for n in dir(xspec) if n.startswith('XS')])

for name in xspeclmodels.__all__:
    if not name.startswith('XS') or name in xsmodels:
        continue

    cls = getattr(xspeclmodels, name)
    ui.add_model(cls)

    logger.info("Adding XSPEC local model: {}".format(name.lower()))
