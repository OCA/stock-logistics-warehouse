from odoo import api, fields, models


class ProductQuantWizard(models.TransientModel):
    _name = "product.quant.wizard"
    _description = "Product Quant Wizard"

    product_id = fields.Many2one("product.product")
    stock_quant_ids = fields.Many2many(
        "stock.quant", compute="_compute_stock_quant_ids"
    )

    @api.depends("product_id")
    def _compute_stock_quant_ids(self):
        for rec in self:
            rec.stock_quant_ids = rec.product_id.stock_quant_ids.filtered(
                lambda x: x.location_id.usage in ["internal", "transit"]
                if self.env.user.has_group(
                    "sale_stock_on_hand_popup.group_show_transit_location_stock_wizard"
                )
                else x.location_id.usage == "internal"
            )
