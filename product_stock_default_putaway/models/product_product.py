# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.fields import first


class ProductProduct(models.Model):
    _inherit = "product.product"

    default_putaway_location_id = fields.Many2one(
        comodel_name="stock.location",
        compute="_compute_default_putaway_location_id",
        help="This ",
    )

    @api.depends_context("location", "warehouse_id")
    @api.depends("putaway_rule_ids")
    def _compute_default_putaway_location_id(self):
        """
        This will compute the default putaway location for product
        depending on product putaway rules.

        By default, the default rule is taken from the first warehouse
        stock location as input location.

        But, as for the quantities computation, we can pass:
          - warehouse_id
          - location
        through the context in order to get the right result
        (e.g.: from stock moves)
        """
        location = self.env.context.get("location", self.env["stock.location"].browse())
        warehouse = self.env.context.get(
            "warehouse_id", self.env["stock.warehouse"].browse()
        )
        if not location and not warehouse:
            warehouse = self.env["stock.warehouse"].search([], limit=1)
        if not location:
            location = warehouse.lot_stock_id
        products_without_location = self.browse()
        for product in self:
            putaway = first(
                product.putaway_rule_ids.filtered_domain(
                    [("location_in_id", "child_of", location.id)]
                )
            )
            if putaway:
                product.default_putaway_location_id = putaway.location_out_id
            else:
                products_without_location |= product
        if products_without_location:
            products_without_location.default_putaway_location_id = self.env[
                "stock.location"
            ].browse()
