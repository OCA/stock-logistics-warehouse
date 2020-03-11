# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    common_dest_move_ids = fields.Many2many(
        "stock.move",
        compute="_compute_common_dest_move_ids",
        help="All the stock moves having a chained destination move sharing the"
        " same picking as the actual move's destination move",
    )

    @api.depends(
        "move_dest_ids",
        "move_dest_ids.picking_id",
        "move_dest_ids.picking_id.move_lines",
        "move_dest_ids.picking_id.move_lines.move_orig_ids",
    )
    def _compute_common_dest_move_ids(self):
        sql = """SELECT smmr.move_orig_id move_id
            , array_agg(smmr2.move_orig_id) common_move_dest_ids
            FROM stock_move_move_rel smmr
            , stock_move sm_dest
            , stock_picking sp
            , stock_move sm_pick
            , stock_move_move_rel smmr2
            WHERE smmr.move_dest_id = sm_dest.id
            AND sm_dest.picking_id = sp.id
            AND sp.id = sm_pick.picking_id
            AND sm_pick.id = smmr2.move_dest_id
            AND smmr.move_orig_id != smmr2.move_orig_id
            AND smmr.move_orig_id IN %s
            GROUP BY smmr.move_orig_id;
        """
        self.env.cr.execute(sql, (tuple(self.ids),))
        res = {
            row.get("move_id"): row.get("common_move_dest_ids")
            for row in self.env.cr.dictfetchall()
        }
        for move in self:
            common_move_ids = res.get(move.id)
            if common_move_ids:
                move.common_dest_move_ids = [(6, 0, common_move_ids)]
            else:
                move.common_dest_move_ids = [(5, 0, 0)]
