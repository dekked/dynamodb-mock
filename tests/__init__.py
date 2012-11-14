# -*- coding: utf-8 -*-

import logging
from ddbmock import config, utils

# Much too slow otherwise
config.DELAY_CREATING = 0.02
config.DELAY_UPDATING = 0.02
config.DELAY_DELETING = 0.02

# Configure logging
utils.tp_logger.addHandler(logging.StreamHandler())
