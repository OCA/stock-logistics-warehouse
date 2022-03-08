# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.location_id = False
        self.lot_id = False
        return super()._onchange_product_id()

    @api.onchange("lot_id")
    def _onchange_lot_id(self):
        self.location_id = False
