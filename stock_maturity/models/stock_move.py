# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _update_reserved_quantity(self, *args, **kwargs):
        # Avoid reserving quants that aren't mature
        if self.product_id.use_maturity_date:
            return super(
                StockMove, self.with_context(with_maturity=self.date)
            )._update_reserved_quantity(*args, **kwargs)
        return super()._update_reserved_quantity(*args, **kwargs)

    def _get_available_quantity(self, *args, **kwargs):
        # Avoid planning on quants that aren't mature
        if self.product_id.use_maturity_date:
            return super(
                StockMove, self.with_context(with_maturity=self.date)
            )._get_available_quantity(*args, **kwargs)
        return super()._get_available_quantity(*args, **kwargs)
