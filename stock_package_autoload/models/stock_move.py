from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero


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
        rounding = self.product_id.uom_id.rounding
        # Lines added in the view do not have a Lot,
        # but they have a quant to avoid duplicates.
        # See `stock.move.line.quant_id`
        view_lots = self.move_line_ids.quant_id.lot_id
        current_lots = self.move_line_ids.mapped("lot_id") | view_lots
        lots_to_qty = {}
        for current_lot in current_lots:
            move_lines = self.move_line_ids.filtered(
                lambda line, lot=current_lot: line.lot_id == lot
            )
            if not move_lines:
                # The line has been added using `quant_id`
                # and does not have a Lot yet, search it by quant's Lot
                move_lines = self.move_line_ids.filtered(
                    lambda line, lot=current_lot: line.quant_id.lot_id == lot
                )
            lots_to_qty[current_lot] = sum(move_lines.mapped("quantity"), 0)

        product_quants = self.load_products_from_package_id.quant_ids.filtered(
            lambda q, product=self.product_id: q.product_id == product
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
            lot = quant.lot_id
            quantity = quant.quantity
            # Remove already selected quantity for this lot
            already_selected_qty = lots_to_qty.get(lot, 0)
            if not float_is_zero(already_selected_qty, precision_rounding=rounding):
                quantity -= already_selected_qty
                if float_compare(quantity, 0, precision_rounding=rounding) <= 0:
                    # Skip negative quantities or exhausted lots
                    continue

            data = common_line_data.copy()
            data.update(
                {
                    "quant_id": quant.id,
                    "quantity": quantity,
                    "product_uom_id": quant.product_uom_id.id,
                    "lot_id": lot.id,
                }
            )
            command_list.append(fields.Command.create(data))
        self.move_line_ids = command_list
        self.load_products_from_package_id = False
