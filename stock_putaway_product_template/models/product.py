# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2021 Tecnativa - Víctor Martínez

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_view_related_putaway_rules(self):
        self.ensure_one()
        domain = [
            "|",
            "|",
            ("product_tmpl_id", "=", self.id),
            ("category_id", "=", self.categ_id.id),
            ("product_id.product_tmpl_id", "=", self.id),
        ]
        return self._get_action_view_related_putaway_rules(domain)
