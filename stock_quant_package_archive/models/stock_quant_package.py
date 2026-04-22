# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class QuantPackage(models.Model):
    _inherit = "stock.quant.package"

    active = fields.Boolean(default=True)
