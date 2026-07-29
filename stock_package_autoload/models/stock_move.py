from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    package_domain = fields.Binary(
        compute="_compute_package_domain",
        readonly=True,
        store=False,
    )
    load_products_from_package_id = fields.Many2one(
        "stock.quant.package",
        string="Add package contents",
        help="Autoresets after use",
    )

    def _package_domain(self):
        self.ensure_one()
        to_return = (
            [("quant_ids.product_id", "=", self.product_id.id)]
            if self.product_id
            else []
        )
        return to_return

    def _compute_package_domain(self):
        """
        There's no need to compute this field if the current user doesn't have the
        necessary group
        """
        if not self.env.user.has_group("stock.group_tracking_lot"):
            self.write({"package_domain": "[]"})
            return
        for sm in self:
            sm.package_domain = sm._package_domain()

    @api.onchange("load_products_from_package_id")
    def _onchange_load_products_from_package_id(self):
        """Automatically load all items contained in the selected package.
        Once the items have been added, the package is deleted.
        The same serials cannot be selected more than once.
        """
        current_lots = self.move_line_ids.mapped("lot_id")
        product_quants = self.load_products_from_package_id.quant_ids.filtered(
            lambda q, lots=current_lots: q.lot_id not in lots
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
        data_list = []
        for quant in product_quants:
            data = common_line_data.copy()
            data.update(
                {
                    "qty_done": quant.quantity,
                    "product_uom_id": quant.product_uom_id.id,
                    "lot_id": quant.lot_id.id,
                }
            )
            data_list.append(data)
        self.env["stock.move.line"].create(data_list)
        self.load_products_from_package_id = False
