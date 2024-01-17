from odoo import _, models


class Product(models.Model):
    _inherit = "product.product"

    def action_open_quants_show_products(self):
        res = self.action_open_quants()

        res.update(
            {
                "name": _("Stock Lines"),
                "context": {
                    **res.get("context", {}),
                    "single_product": False,
                    "edit": False,
                },
            }
        )
        return res
