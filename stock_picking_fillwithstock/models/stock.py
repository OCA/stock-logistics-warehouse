# Copyright Jacques-Etienne Baudoux 2016 Camptocamp
# Copyright Iryna Vyshnevska 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import Warning
from itertools import groupby


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_fillwithstock(self):
        # check source location has no children, i.e. we scanned a bin
        self.ensure_one()
        if self.location_id.child_ids:
            raise Warning(_('Please choose a source end location'))
        if self.move_lines:
            raise Warning(_('Moves lines already exists'))
        quants = self.env['stock.quant'].search(
            [
                ('location_id', 'child_of', self.location_id.id),
                ('quantity', '>', 0.0),
            ]
        )
        products = {}
        available = False
        for product, quant in groupby(quants, lambda r: r.product_id):
            # we need only one quant per product
            quant = list(quant)[0]
            qty = quant._get_available_quantity(
                quant.product_id,
                self.location_id,
            )
            if qty:
                available = True
                if quant.product_id.id not in products:
                    products[quant.product_id.id] = {
                        'picking_id': self.id,
                        'product_id': quant.product_id.id,
                        'name': quant.product_id.partner_ref,
                        'product_uom_qty': qty,
                        'product_uom': quant.product_uom_id.id,
                        'picking_type_id': self.picking_type_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                    }
                else:
                    products[quant.product_id.id]['product_uom_qty'] += qty
        move_obj = self.env['stock.move']
        if not available:
            raise Warning(_('Nothing to move'))
        for data in products.values():
            move_obj.create(data)
        self.action_confirm()
        self.action_assign()
        return True
