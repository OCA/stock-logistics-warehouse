# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import tools

_logger = logging.getLogger(__name__)

try:
    from openupgradelib import openupgrade
    EXTERNAL_DEPENDENCY_BINARY_OPENUPGRADELIB_PATH = tools.find_in_path(
        'openupgradelib')
except (ImportError, IOError) as err:
    _logger.debug(err)


def pre_init_hook(cr):
    """Loaded before installing the module.
    """
    openupgrade.update_module_names(
        cr,
        [('stock_location_restrict_group',
          'stock_location_restrict_procurement_group')],
        merge_modules=True
    )
