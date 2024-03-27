from odoo.addons.mrp.models.mrp_production import MrpProduction
from odoo import fields
from odoo.exceptions import UserError


MrpProduction._original_update_raw_moves = MrpProduction._update_raw_moves


# Override
def _update_raw_moves_patched(self, factor):
    module = (
        self.env["ir.module.module"]
        .sudo()
        .search([("name", "=", "stock_reservation_method_mrp")], limit=1)
    )
    if module.state not in ("to install", "installed"):
        return MrpProduction._original_update_raw_moves(self, factor)
    self.ensure_one()
    update_info = []
    for move in self.move_raw_ids.filtered(lambda m: m.state not in ("done", "cancel")):
        old_qty = move.product_uom_qty
        new_qty = old_qty * factor
        move.write({"product_uom_qty": new_qty})
        # START OF HOOK
        if (
            move._should_bypass_reservation()
            or move.picking_type_id.reservation_method == "at_confirm"
            or (move.reservation_date and move.reservation_date <= fields.Date.today())
        ):
            move._action_assign()
        # END OF HOOK
        update_info.append((move, old_qty, new_qty))
    return update_info


MrpProduction._update_raw_moves = _update_raw_moves_patched

MrpProduction._original_generate_backorder_productions = (
    MrpProduction._generate_backorder_productions
)


# Override
# flake8: noqa: C901
def _generate_backorder_productions_patched(self, close_mo=True):
    module = (
        self.env["ir.module.module"]
        .sudo()
        .search([("name", "=", "stock_reservation_method_mrp")], limit=1)
    )
    if module.state not in ("to install", "installed"):
        return MrpProduction._original_generate_backorder_productions(self, close_mo)
    backorders = self.env["mrp.production"]
    for production in self:
        if production.backorder_sequence == 0:  # Activate backorder naming
            production.backorder_sequence = 1
        production.name = self._get_name_backorder(
            production.name, production.backorder_sequence
        )
        backorder_mo = production.copy(default=production._get_backorder_mo_vals())
        if close_mo:
            production.move_raw_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            ).write(
                {
                    "raw_material_production_id": backorder_mo.id,
                }
            )
            production.move_finished_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            ).write(
                {
                    "production_id": backorder_mo.id,
                }
            )
        else:
            new_moves_vals = []
            for move in production.move_raw_ids | production.move_finished_ids:
                if not move.additional:
                    qty_to_split = (
                        move.product_uom_qty
                        - move.unit_factor * production.qty_producing
                    )
                    qty_to_split = move.product_uom._compute_quantity(
                        qty_to_split, move.product_id.uom_id, rounding_method="HALF-UP"
                    )
                    move_vals = move._split(qty_to_split)
                    if not move_vals:
                        continue
                    if move.raw_material_production_id:
                        move_vals[0]["raw_material_production_id"] = backorder_mo.id
                    else:
                        move_vals[0]["production_id"] = backorder_mo.id
                    # START HOOK
                    move_vals[0]["reservation_date"] = move.reservation_date
                    # END HOOK
                    new_moves_vals.append(move_vals[0])
            self.env["stock.move"].create(new_moves_vals)
        backorders |= backorder_mo

        # We need to adapt `duration_expected` on both the original workorders
        # and their backordered workorders. To do that, we use the original
        # `duration_expected` and the
        # ratio of the quantity really produced and the quantity to produce.
        ratio = production.qty_producing / production.product_qty
        for workorder in production.workorder_ids:
            workorder.duration_expected = workorder.duration_expected * ratio
        for workorder in backorder_mo.workorder_ids:
            workorder.duration_expected = workorder.duration_expected * (1 - ratio)

    # As we have split the moves before validating them, we need to 'remove' the
    # excess reservation
    if not close_mo:
        raw_moves = self.move_raw_ids.filtered(lambda m: not m.additional)
        raw_moves._do_unreserve()
        for sml in raw_moves.move_line_ids:
            try:
                q = self.env["stock.quant"]._update_reserved_quantity(
                    sml.product_id,
                    sml.location_id,
                    sml.qty_done,
                    lot_id=sml.lot_id,
                    package_id=sml.package_id,
                    owner_id=sml.owner_id,
                    strict=True,
                )
                reserved_qty = sum([x[1] for x in q])
                reserved_qty = sml.product_id.uom_id._compute_quantity(
                    reserved_qty, sml.product_uom_id
                )
            except UserError:
                reserved_qty = 0
            sml.with_context(
                bypass_reservation_update=True
            ).product_uom_qty = reserved_qty
        raw_moves._recompute_state()
    # Confirm only productions with remaining components
    backorders.filtered(lambda mo: mo.move_raw_ids).action_confirm()
    # START HOOK
    backorders.filtered(
        lambda mo: mo.move_raw_ids
        and mo.picking_type_id.reservation_method == "at_confirm"
    ).action_assign()
    # END HOOK

    # Remove the serial move line without reserved quantity. Post inventory will
    # assigned all the non done moves So those move lines are duplicated.
    backorders.move_raw_ids.move_line_ids.filtered(
        lambda ml: ml.product_id.tracking == "serial" and ml.product_qty == 0
    ).unlink()
    backorders.move_raw_ids._recompute_state()

    for production, backorder_mo in zip(self, backorders):
        first_wo = self.env["mrp.workorder"]
        for old_wo, wo in zip(production.workorder_ids, backorder_mo.workorder_ids):
            wo.qty_produced = max(old_wo.qty_produced - old_wo.qty_producing, 0)
            if wo.product_tracking == "serial":
                wo.qty_producing = 1
            else:
                wo.qty_producing = wo.qty_remaining
            if wo.qty_producing == 0:
                wo.action_cancel()
            if not first_wo and wo.state != "cancel":
                first_wo = wo
        first_wo.state = "ready"
    return backorders


MrpProduction._generate_backorder_productions = _generate_backorder_productions_patched
