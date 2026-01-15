# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from collections.abc import Iterable

from odoo import api, fields, models
from odoo.fields import Domain


class StockLot(models.Model):
    _inherit = "stock.lot"

    current_partner_id = fields.Many2one(
        "res.partner",
        string="Current Partner Location",
        compute="_compute_current_partner_id",
        search="_search_current_partner_id",
    )

    def _compute_current_partner_id(self):
        serial_lots = self.filtered(
            lambda lt: lt.product_id and lt.product_id.tracking == "serial"
        )
        non_serial_lots = self - serial_lots
        non_serial_lots.current_partner_id = False
        if not serial_lots:
            return
        moves_by_lot = serial_lots._find_move_ids_by_lot()
        for lot in serial_lots:
            move_ids = moves_by_lot.get(lot.id) or []
            if not move_ids:
                lot.current_partner_id = False
                continue
            moves = self.env["stock.move"].browse(move_ids)
            if not moves:
                lot.current_partner_id = False
                continue
            last_move = max(moves, key=lambda m: m.date)
            partner = False
            picking = last_move.picking_id
            # Dropship → sale/purchase partner
            if picking and picking.is_dropship and picking.sale_id:
                partner = picking.sale_id.partner_id
            elif (
                picking and last_move._is_dropshipped_returned() and picking.purchase_id
            ):
                partner = picking.purchase_id.partner_id
            else:
                partner = last_move.partner_id
            # Internal destination → warehouse partner
            if (
                last_move.location_dest_id
                and last_move.location_dest_id.usage == "internal"
            ):
                warehouse = last_move.location_dest_id._get_warehouse()
                if warehouse and warehouse.partner_id:
                    partner = warehouse.partner_id

            lot.current_partner_id = partner or False

    def _find_move_ids_by_lot(self, lot_path=None, moves_by_lot=None):
        if lot_path is None:
            lot_path = set()
        domain = [
            ("lot_id", "in", self.ids),
            ("state", "=", "done"),
        ]
        move_lines = self.env["stock.move.line"].search(domain)
        move_lines = move_lines.filtered(
            lambda ll: ll.location_id.id != ll.location_dest_id.id
        )
        move_lines_map = {
            lot_id: {"producing_lines": set(), "barren_lines": set()}
            for lot_id in move_lines.lot_id.ids
        }
        for line in move_lines:
            if line.produce_line_ids:
                move_lines_map[line.lot_id.id]["producing_lines"].add(line.id)
            else:
                move_lines_map[line.lot_id.id]["barren_lines"].add(line.id)
        if moves_by_lot is None:
            moves_by_lot = {}
        for lot in self:
            move_ids = set()
            if move_lines_map.get(lot.id):
                producing_lines = self.env["stock.move.line"].browse(
                    move_lines_map[lot.id]["producing_lines"]
                )
                barren_lines = self.env["stock.move.line"].browse(
                    move_lines_map[lot.id]["barren_lines"]
                )
                if producing_lines:
                    lot_path.add(lot.id)
                    next_lots = producing_lines.produce_line_ids.lot_id.filtered(
                        lambda ll: ll.id not in lot_path
                    )
                    next_lot_ids = set(next_lots.ids)
                    move_ids.update(
                        *(
                            moves_by_lot.get(lot_id, [])
                            for lot_id in (
                                producing_lines.produce_line_ids.lot_id - next_lots
                            ).ids
                        )
                    )
                    for lot_id, sub_moves in next_lots._find_move_ids_by_lot(
                        lot_path=lot_path, moves_by_lot=moves_by_lot
                    ).items():
                        if lot_id in next_lot_ids:
                            move_ids.update(sub_moves)
                move_ids.update(barren_lines.move_id.ids)
            moves_by_lot[lot.id] = list(move_ids)
        return moves_by_lot

    @api.model
    def _search_current_partner_id(self, operator, value):
        if operator in Domain.NEGATIVE_OPERATORS or not isinstance(value, Iterable):
            return NotImplemented
        StockMoveLine = self.env["stock.move.line"]
        Partner = self.env["res.partner"]
        partner_ids = Partner.search(value).ids
        move_lines = StockMoveLine.search(
            [
                ("state", "=", "done"),
                ("lot_id", "!=", False),
            ]
        )
        last_move_by_lot = {}
        for line in move_lines:
            move = line.move_id
            move_date = move.date
            lot_id = line.lot_id.id
            prev = last_move_by_lot.get(lot_id)
            if not prev or move_date > prev[1]:
                last_move_by_lot[lot_id] = (move, move_date)
        matching_lot_ids = set()
        for lot_id, (move, _) in last_move_by_lot.items():
            partner = False
            picking = move.picking_id
            # Dropship → sale partner
            if picking and picking.is_dropship and picking.sale_id:
                partner = picking.sale_id.partner_id
            else:
                partner = move.partner_id
            # Internal destination → warehouse partner
            if move.location_dest_id and move.location_dest_id.usage == "internal":
                wh = move.location_dest_id._get_warehouse()
                if wh and wh.partner_id:
                    partner = wh.partner_id
            if partner and partner.id in partner_ids:
                matching_lot_ids.add(lot_id)
        if operator in ("any", "=", "in"):
            return [("id", "in", list(matching_lot_ids))]
        return Domain.AND(
            [
                [("id", "not in", list(matching_lot_ids))],
                [("id", "!=", False)],
            ]
        )
