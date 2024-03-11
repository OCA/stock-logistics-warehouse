# Copyright 2015 AvanzOSC - Oihane Crucelaegi
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2020 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    product_selection = fields.Selection(
        selection_add=[("domain", "Filtered Products")],
        ondelete={"domain": "set default"},
    )
    product_domain = fields.Char("Domain", default=[("name", "ilike", "")])

    def action_state_to_in_progress(self):
        for inventory in self:
            if inventory.state != "draft":
                continue
            if inventory.product_selection:
                products = inventory._prepare_inventory_filter()
                if products:
                    inventory.product_ids = [(6, 0, products.ids)]
        return super().action_state_to_in_progress()

    def _prepare_inventory_filter(self):
        # This method is designed to be inherited by other modules
        # such as the OCA module stock_inventory_preparation_filter_pos
        self.ensure_one()
        Product = self.env["product.product"]
        products = Product
        if self.product_selection == "domain":
            domain = safe_eval(self.product_domain)
            products = Product.search(domain)
        return products

    def _get_quants(self, locations):
        if self.product_selection == "domain":
            domain = safe_eval(self.product_domain)
            products = self.env["product.product"].search(domain)
            return self.env["stock.quant"].search([("product_id", "in", products.ids)])
        return super()._get_quants(locations)
