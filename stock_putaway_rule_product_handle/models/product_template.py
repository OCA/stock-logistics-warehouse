# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_view_related_putaway_rules(self):
        new_self = (
            self.with_context(invisible_handle=False)
            if self.env.user.has_group("stock.group_stock_manager")
            else self
        )
        return super(ProductTemplate, new_self).action_view_related_putaway_rules()

    @api.model
    def _get_action_view_related_putaway_rules(self, domain):
        res = super()._get_action_view_related_putaway_rules(domain)
        context = res.get("context")
        if not context:
            res["context"] = {
                "invisible_handle": self.env.context.get("invisible_handle")
            }
        return res
