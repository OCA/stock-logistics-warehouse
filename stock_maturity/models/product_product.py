# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def action_open_quants(self):
        # Hide the `maturity_date` column if not needed.
        if not any(product.use_maturity_date for product in self):
            self = self.with_context(hide_maturity_date=True)
        return super().action_open_quants()
