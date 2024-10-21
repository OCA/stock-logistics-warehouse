# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("active")
    def _check_active_stock_archive_constraint(self):
        self.product_variant_ids._check_active_stock_archive_constraint()
