# Copyright 2015 AvanzOSC - Oihane Crucelaegi
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2020 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _selection_filter(self):
        """ Get the list of filter allowed according to the options checked
        in 'Settings / Warehouse'. """
        res_filter = [
            ("products", _("All products")),
            ("categories", _("Selected Categories")),
            ("domain", _("Filtered Products")),
        ]
        if self.user_has_groups("stock.group_production_lot"):
            res_filter.append(("lots", _("Selected Lots")))
        return res_filter

    filter = fields.Selection(
        string="Inventory of",
        selection="_selection_filter",
        required=True,
        default="products",
        help="If you do an entire inventory, you can choose 'All Products' and "
        "it will prefill the inventory with the current stock.  If you "
        "only do some products (e.g. Cycle Counting) you can choose "
        "'Manual Selection of Products' and the system won't propose "
        "anything.  You can also let the system propose for a single "
        "product / lot /... ",
    )
    categ_ids = fields.Many2many(
        comodel_name="product.category",
        relation="rel_inventories_categories",
        column1="inventory_id",
        column2="category_id",
        string="Categories",
    )
    lot_ids = fields.Many2many(
        comodel_name="stock.production.lot",
        relation="rel_inventories_lots",
        column1="inventory_id",
        column2="lot_id",
        string="Lots",
    )
    product_domain = fields.Char("Domain", default=[("name", "ilike", "")])

    def _action_start(self):
        Product = self.env["product.product"]
        for inventory in self:
            products = Product.browse()
            if inventory.state != "draft":
                continue
            if inventory.filter == "categories":
                products = Product.search([("categ_id", "in", inventory.categ_ids.ids)])
            if inventory.filter == "lots":
                products = inventory.lot_ids.mapped("product_id")
            if inventory.filter == "domain":
                domain = safe_eval(inventory.product_domain)
                products = Product.search(domain)
            if products:
                inventory.product_ids = [(6, 0, products.ids)]
        return super()._action_start()
