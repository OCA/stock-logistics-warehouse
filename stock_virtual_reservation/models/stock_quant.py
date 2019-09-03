# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    # def _get_available_quantity(
    #     self,
    #     product_id,
    #     location_id,
    #     lot_id=None,
    #     package_id=None,
    #     owner_id=None,
    #     strict=False,
    #     allow_negative=False,
    # ):
    #     pass
