# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.
import logging

from odoo import SUPERUSER_ID, api

from odoo.addons.account_move_line_stock_info.hooks import post_init_hook

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Trigger again the post_init_hook")
    env = api.Environment(cr, SUPERUSER_ID, {})
    post_init_hook(cr, env.registry)
