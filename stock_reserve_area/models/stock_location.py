# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    reserve_area_ids = fields.Many2many(
        "stock.reserve.area",
        relation="stock_reserve_area_stock_location_rel",
        column1="location_id",
        column2="reserve_area_id",
        readonly=True,
    )

    def write(self, vals):
        res = super().write(vals)
        if not vals.get("reserve_area_ids"):
            return res
        new_reserve_areas = (
            self.env["stock.reserve.area"].sudo().browse(vals["reserve_area_ids"])
        )
        self._update_impacted_moves(new_reserve_areas)
        return res

    def _update_impacted_moves(self, new_reserve_areas):
        """If a location is moved outside/inside an area we have to check stock_moves"""
        for loc in self:
            moves_poss_impacted = self.env["stock.move"].search(
                [
                    "|",
                    ("location_id", "=", loc.id),
                    ("location_dest_id", "=", loc.id),
                    ("state", "in", ("confirmed", "waiting", "partially_available")),
                ]
            )
            for move in moves_poss_impacted:
                for reserve_area in new_reserve_areas:
                    if move._is_out_area(reserve_area):
                        move.reserve_area_line_ids += self.env[
                            "stock.move.reserve.area.line"
                        ].create(
                            {
                                "move_id": move.id,
                                "reserve_area_id": reserve_area.id,
                            }
                        )
