from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def action_open_quants_show_products(self):
        self.ensure_one()
        return {
            "name": self.display_name,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "product.quant.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {
                **self.env.context,
                "default_product_id": self.id,
            },
        }
