# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError

MSG_ERROR_HAS_STOCK = (
    "Unable to archive the following product(s) "
    "because there is stock left in at least one warehouse: "
)
MSG_ERROR_PER_PRODUCT = "\nFor the product {}:"
MSG_ERROR_PER_WH = "\n- {} in warehouse {} ({})"


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_all_stock_levels(self):
        result = []
        all_warehouses = self.env["stock.warehouse"].sudo().search([])
        for wh in all_warehouses:
            qty_available = self.with_context(warehouse=wh.id).qty_available
            if qty_available:
                result += [(wh, qty_available)]
        return result

    def _check_has_quantities_archive(self):
        result = []
        for rec in self:
            stock_levels = rec._get_all_stock_levels()
            if stock_levels:
                result += [(rec, stock_levels)]
        return result

    def _format_errors_archive(self, quantities):
        msg = ""
        for product, stock_levels in quantities:
            msg += _(MSG_ERROR_PER_PRODUCT).format(product.display_name)
            for wh, stock_level in stock_levels:
                msg += _(MSG_ERROR_PER_WH).format(
                    stock_level, wh.name, wh.company_id.name
                )
        return msg

    @api.model
    def write(self, vals):
        if "active" in vals.keys() and not vals["active"]:
            quantities = self.sudo()._check_has_quantities_archive()
            if quantities:
                raise ValidationError(
                    MSG_ERROR_HAS_STOCK + self.sudo()._format_errors_archive(quantities)
                )
        return super().write(vals)
