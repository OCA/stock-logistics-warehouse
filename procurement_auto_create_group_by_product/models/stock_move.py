# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from itertools import groupby

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _merge_moves(self, merge_into=False):
        sorted_moves_by_rule = sorted(self, key=lambda m: m.rule_id.id)
        res_moves = self.browse()
        for _rule, move_list in groupby(
            sorted_moves_by_rule, key=lambda m: m.rule_id.id
        ):
            moves = self.browse(m.id for m in move_list)
            res_moves |= super(StockMove, moves)._merge_moves(merge_into=merge_into)
        return res_moves

    def _prepare_merge_moves_distinct_fields(self):
        result = super()._prepare_merge_moves_distinct_fields()
        if self.rule_id.auto_create_group_by_product:
            # Allow to merge moves on a pick operation having different
            # deadlines
            if "date_deadline" in result:
                result.remove("date_deadline")
        return result
