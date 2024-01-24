# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, exceptions, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _check_restrictions(self):
        # returned_move_ids in stock.move
        # split_from in stock.move
        for move in self.move_lines:
            move._check_restrictions()

    def action_revert_recreate(self):
        self.ensure_one()
        pick = self
        pick._check_restrictions()
        msg = _(
            "Too bad. This picking cannot be returned because the products "
            "are not available in the destination location"
        )
        # Create return picking
        StockReturnPicking = self.env["stock.return.picking"]
        default_data = StockReturnPicking.with_context(
            active_model="stock.picking", active_id=pick.id
        ).default_get(
            [
                "move_dest_exists",
                "original_location_id",
                "product_return_moves",
                "parent_location_id",
                "location_id",
            ]
        )
        default_data.update({"location_id": pick.location_id.id})
        return_wiz = StockReturnPicking.create(default_data)
        return_wiz._onchange_picking_id()
        for rm in return_wiz.product_return_moves:
            sm = pick.move_lines.filtered(lambda x: x.product_id.id == rm.product_id.id)
            if rm.quantity < sm.product_uom_qty:
                raise exceptions.UserError(msg)
        try:
            res = return_wiz.create_returns()
        except exceptions.UserError as e:
            raise exceptions.UserError(e) from e

        return_pick = self.env["stock.picking"].browse(res["res_id"])

        # Validate picking
        return_pick.action_set_quantities_to_reservation()
        return_pick._action_done()
        new_pick = pick.copy()
        new_pick.action_assign()
        action = self.env.ref("stock.action_picking_tree_all")
        result = action.read()[0]
        res = self.env.ref("stock.view_picking_form", False)
        result["views"] = [(res and res.id or False, "form")]
        result["res_id"] = new_pick.id
        return result
