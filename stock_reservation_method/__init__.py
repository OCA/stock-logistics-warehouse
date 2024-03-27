from . import models
from .init_hooks import pre_init_hook
from odoo.addons.stock.models.stock_move import StockMove
from odoo.tools.misc import clean_context
from odoo import fields


StockMove._original_action_confirm = StockMove._action_confirm


# Override
def _action_confirm_patched(self, merge=True, merge_into=False):
    """Confirms stock move or put it in waiting if it's linked
    to another move.
    :param: merge: According to this boolean, a newly confirmed
    move will be merged
    in another move of the same picking sharing its characteristics.
    """
    module = (
        self.env["ir.module.module"]
        .sudo()
        .search([("name", "=", "stock_reservation_method")], limit=1)
    )
    if module.state not in ("to install", "installed"):
        return StockMove._original_action_confirm(self, merge, merge_into)
    move_create_proc = self.env["stock.move"]
    move_to_confirm = self.env["stock.move"]
    move_waiting = self.env["stock.move"]

    to_assign = {}
    for move in self:
        if move.state != "draft":
            continue
        # if the move is preceeded, then it's waiting (
        # if preceeding move is done, then action_assign
        # has been called already and its state is already available)
        if move.move_orig_ids:
            move_waiting |= move
        else:
            if move.procure_method == "make_to_order":
                move_create_proc |= move
            else:
                move_to_confirm |= move
        if move._should_be_assigned():
            key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
            if key not in to_assign:
                to_assign[key] = self.env["stock.move"]
            to_assign[key] |= move

    # create procurements for make to order moves
    procurement_requests = []
    for move in move_create_proc:
        values = move._prepare_procurement_values()
        origin = move._prepare_procurement_origin()
        procurement_requests.append(
            self.env["procurement.group"].Procurement(
                move.product_id,
                move.product_uom_qty,
                move.product_uom,
                move.location_id,
                move.rule_id and move.rule_id.name or "/",
                origin,
                move.company_id,
                values,
            )
        )
    self.env["procurement.group"].run(
        procurement_requests,
        raise_user_error=not self.env.context.get("from_orderpoint"),
    )

    move_to_confirm.write({"state": "confirmed"})
    (move_waiting | move_create_proc).write({"state": "waiting"})
    # procure_method sometimes changes with
    # certain workflows so just in case, apply to all moves
    (move_to_confirm | move_waiting | move_create_proc).filtered(
        lambda m: m.picking_type_id.reservation_method == "at_confirm"
    ).write({"reservation_date": fields.Date.today()})

    # assign picking in batch for all
    # confirmed move that share the same details
    for moves in to_assign.values():
        moves.with_context(clean_context(moves.env.context))._assign_picking()
    self._push_apply()
    self._check_company()
    moves = self
    if merge:
        moves = self._merge_moves(merge_into=merge_into)
    # call `_action_assign` on every confirmed move
    # which location_id bypasses the reservation + those
    # expected to be auto-assigned
    moves.filtered(
        lambda move: not move.picking_id.immediate_transfer
        and move.state in ("confirmed", "partially_available")
        and (
            move._should_bypass_reservation()
            or move.picking_type_id.reservation_method == "at_confirm"
            or (move.reservation_date and move.reservation_date <= fields.Date.today())
        )
    )._action_assign()
    return moves


StockMove._action_confirm = _action_confirm_patched
