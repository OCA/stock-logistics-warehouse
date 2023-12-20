# Copyright Akretion (http://www.akretion.com/)

from odoo import models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    def ui_goto_packaging_view(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "product.action_packaging_view"
        )
        action["context"] = {
            "search_default_product_id": self.product_id.id,
        }
        variants = self.product_id.product_tmpl_id.product_variant_ids
        action["domain"] = f"[('product_id', 'in', {variants.ids})]"
        return action
