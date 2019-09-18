# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
import math


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_quantities_dict(
            self, lot_id, owner_id, package_id,
            from_date=False, to_date=False):
        res = super()._compute_quantities_dict(
            lot_id, owner_id, package_id, from_date=from_date, to_date=to_date)
        packs = self.filtered('pack_ok')
        for product in packs.with_context(prefetch_fields=False):
            pack_qty_available = []
            pack_virtual_available = []
            for subproduct in product.pack_line_ids:
                subproduct_stock = subproduct.product_id
                sub_qty = subproduct.quantity
                if sub_qty:
                    pack_qty_available.append(math.floor(
                        subproduct_stock.qty_available / sub_qty))
                    pack_virtual_available.append(math.floor(
                        subproduct_stock.virtual_available / sub_qty))
            res[product.id] = {
                'qty_available': (
                    pack_qty_available and min(pack_qty_available) or False),
                'incoming_qty': 0,
                'outgoing_qty': 0,
                'virtual_available': (
                    pack_virtual_available and
                    min(pack_virtual_available) or False),
            }
        return res
