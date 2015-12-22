# -*- coding: utf-8 -*-
# © 2015 ClearCorp S.A.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockMove(models.Model):
        _inherit = "stock.move"

        @api.multi
        def action_consume(
                self, product_qty, location_id=False, restrict_lot_id=False,
                restrict_partner_id=False, consumed_for=False):
            res = super(StockMove, self).action_consume(
                product_qty, location_id=location_id,
                restrict_lot_id=restrict_lot_id,
                restrict_partner_id=restrict_partner_id,
                consumed_for=consumed_for)
            if 'reserve_stock' in self._context.keys() and \
                    self._context['reserve_stock'] is True and \
                    consumed_for is False:
                vals = {
                    'product_id': self.product_id.id,
                    'product_uom': self.product_uom.id,
                    'product_uom_qty': self.product_uom_qty,
                    'name': self.name,
                    'location_id': self.location_dest_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'note': self.note,
                    'product_uos_qty': self.product_uos_qty,
                    'product_uos': self.product_uos.id,
                    'price_unit': self.price_unit,
                    'restrict_partner_id': restrict_partner_id,
                    'restrict_lot_id': restrict_lot_id
                }
                reserve_stock_obj = self.env['stock.reservation'].create(vals)
                reserve_stock_obj.reserve()
            return res
