# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    auto_create_group_by_product = fields.Boolean(string="Procurement Group by Product")

    def _get_auto_procurement_group(self, product):
        if self.auto_create_group_by_product:
            if product.auto_create_procurement_group_ids:
                return fields.first(product.auto_create_procurement_group_ids)
        return super()._get_auto_procurement_group(product)

    def _prepare_auto_procurement_group_data(self, product):
        result = super()._prepare_auto_procurement_group_data(product)
        if self.auto_create_group_by_product:
            result["product_id"] = product.id
            result["partner_id"] = False
        return result
