#
# This code is placed into the PUBLIC DOMAIN.
# It was written by Douglas Burke dburke.gw@gmail.com
#
"""
Provide access to the local models when using the Sherpa UI
layer.

The added models are reported to the user using Sherpa's logger
at the logging.INFO level.

"""

from sherpa.astro import ui
import logging

import xspeclmodels


logger = logging.getLogger('sherpa')

for name in xspeclmodels.__all__:
    if not name.startswith('XS'):
        continue

    cls = getattr(xspeclmodels, name)
    ui.add_model(cls)

    logger.info("Adding XSPEC local model: {}".format(name.lower()))
