# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

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
            quants = self.browse()
            minimum_expiry_shelf_life = (
                self.env.context.get('minimum_expiry_shelf_life')
            )
            for rec in res:
                if rec.lot_id.removal_date > minimum_expiry_shelf_life:
                    quants |= rec
            return quants

        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_assign(self):
        for rec in self:
            if rec.picking_id.group_id.sale_id:
                min_shelf_life_date = (
                    rec.picking_id.group_id._get_lot_min_expiration_date()
                )
                return super(StockMove,
                             rec.with_context(
                                 minimum_expiry_shelf_life=min_shelf_life_date
                             ))._action_assign()
            else:
                return super()._action_assign()
