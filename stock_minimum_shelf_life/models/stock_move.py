# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as dt_fmt
from odoo import models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _gather(self, product_id, location_id, lot_id=None, package_id=None,
                owner_id=None, strict=False):
        res = super()._gather(
            product_id, location_id, lot_id=lot_id,
            package_id=package_id, owner_id=owner_id, strict=strict
        )

        # filter the quants that respect the minimum shelf life date
        if "minimum_expiry_shelf_life" in self.env.context:
            minimum_expiry_shelf_life = (
                self.env.context.get('minimum_expiry_shelf_life')
            )
            quants = self.search(
                [('id', 'in', res.ids),
                 ('lot_id.removal_date', '>', minimum_expiry_shelf_life)
                 ]
            )
            return quants

        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_assign(self):
        proc_sales_moves = self.filtered(
            lambda m: m.picking_id.group_id.sale_id
        )
        groups = proc_sales_moves.mapped('picking_id.group_id')
        dates = {}
        for k, v in [
                (g._get_lot_min_expiration_date().strftime(dt_fmt),
                 g.id) for g in groups]:
            dates.setdefault(k, []).append(v)

        for dt, groups_ids in dates.items():
            min_shelf_life_date = datetime.strptime(dt, dt_fmt)
            moves_filtered = proc_sales_moves.filtered(
                lambda m: m.picking_id.group_id.id in groups_ids
            )
            super(StockMove, moves_filtered.with_context(
                minimum_expiry_shelf_life=min_shelf_life_date
            ))._action_assign()

        # run action_assign on other moves
        super(StockMove, self - proc_sales_moves)._action_assign()
