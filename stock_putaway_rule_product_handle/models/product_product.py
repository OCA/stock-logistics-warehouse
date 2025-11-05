# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_view_related_putaway_rules(self):
        new_self = (
            self.with_context(invisible_handle=False)
            if self.env.user.has_group("stock.group_stock_manager")
            else self
        )
        return super(ProductProduct, new_self).action_view_related_putaway_rules()
