# -*- coding: utf-8 -*-

from ddbmock import config

_store_mod = __import__(config.STORAGE_ENGINE_NAME, globals(), locals(), ['Store'], 1)
Store = _store_mod.Store
