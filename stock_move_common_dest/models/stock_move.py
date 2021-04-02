# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    common_dest_move_ids = fields.Many2many(
        "stock.move",
        compute="_compute_common_dest_move_ids",
        search="_search_compute_dest_move_ids",
        help="All the stock moves having a chained destination move sharing the"
        " same picking as the actual move's destination move",
    )

    def _common_dest_move_query(self):
        sql = """
        SELECT
            sm_orig.id as move_id,
            array_agg(sm.id) as common_move_dest_ids
        FROM
            stock_move sm_dest,
            stock_move sm_dest2,
            stock_move sm_orig,
            stock_move sm
        WHERE
            -- takes the desination move
            sm_orig.move_dest_id = sm_dest.id
            -- takes all the moves into the same picking as the destination
            --  move
            AND sm_dest2.picking_id = sm_dest.picking_id
            -- takes the move where destiation is a move into the same picking
            -- as the destination move
            AND sm.move_dest_id = sm_dest2.id
            AND sm.id != sm_orig.id
            AND sm_orig.id IN %s
            GROUP BY sm_orig.id
        """
        return sql

    @api.depends(
        "picking_id",
        "move_dest_id",
        "move_dest_id.picking_id",
    )
    def _compute_common_dest_move_ids(self):
        sql = self._common_dest_move_query()
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

    def _search_compute_dest_move_ids(self, operator, value):
        moves = self.search([("id", operator, value)])
        if not moves:
            return [("id", "=", 0)]
        sql = self._common_dest_move_query()
        self.env.cr.execute(sql, (tuple(moves.ids),))
        res = [
            move_dest_id
            for row in self.env.cr.dictfetchall()
            for move_dest_id in row.get("common_move_dest_ids") or []
        ]
        return [("id", "in", res)]
