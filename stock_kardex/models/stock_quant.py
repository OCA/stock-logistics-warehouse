# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _update_available_quantity(self, *args, **kwargs):
        result = super()._update_available_quantity(*args, **kwargs)
        # We cannot have fields to depends on to invalidate this
        # computed fields on stock.kardex. But we know that when the quantity
        # of quant changes, we can invalidate the field on the kardex tray.
        self.env['stock.kardex'].invalidate_cache(['kardex_tray_qty'])
        return result
