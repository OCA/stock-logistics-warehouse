from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    load_products_from_package_id = fields.Many2one(
        "stock.quant.package",
        domain="""[
            ("quant_ids.product_id", "=", product_id),
        ]""",
        string="Add package contents",
        help="Add all the products in the selected package to this move.\n"
        "Autoresets after use.",
    )

    @api.onchange("load_products_from_package_id")
    def _onchange_load_products_from_package_id(self):
        """Automatically load all items contained in the selected package.
        Once the items have been added, the package is deleted.
        The same serials cannot be selected more than once.
        """
        self.ensure_one()
        # Lines added in the view do not have a Lot,
        # but they have a quant to avoid duplicates.
        # See `stock.move.line.quant_id`
        view_lots = self.move_line_ids.quant_id.lot_id
        current_lots = self.move_line_ids.mapped("lot_id") | view_lots
        product_quants = self.load_products_from_package_id.quant_ids.filtered(
            lambda q, lots=current_lots, product=self.product_id: (
                q.lot_id not in lots and q.product_id == product
            )
        )
        common_line_data = {
            "move_id": self.id,
            "tracking": self.has_tracking,
            "product_id": self.product_id.id,
            "package_id": self.load_products_from_package_id.id,
            "location_id": self.location_id.id,
            "location_dest_id": self.location_dest_id.id,
            "company_id": self.company_id.id,
        }
        command_list = []
        for quant in product_quants:
            data = common_line_data.copy()
            data.update(
                {
                    "quant_id": quant.id,
                    "quantity": quant.quantity,
                    "product_uom_id": quant.product_uom_id.id,
                    "lot_id": quant.lot_id.id,
                }
            )
            command_list.append(fields.Command.create(data))
        self.move_line_ids = command_list
        self.load_products_from_package_id = False
