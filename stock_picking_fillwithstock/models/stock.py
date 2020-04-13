# Copyright Jacques-Etienne Baudoux 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import Warning


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_fillwithstock(self):
        # check source location has no children, i.e. we scanned a bin
        self.ensure_one()
        if self.location_id.child_ids:
            raise Warning(_('Please choose a source end location'))
        if self.move_lines:
            raise Warning(_('Moves lines already exsits'))
        quants = self.env['stock.quant'].search(
            [
                ('location_id', 'child_of', self.location_id.id),
                ('reservation_id', '=', False),
                ('qty', '>', 0.0),
            ]
        )
        products = {}
        available = False
        for quant in quants:
            if not quant.reservation_id:
                available = True
            if quant.product_id.id not in products:
                products[quant.product_id.id] = {
                    'picking_id': self.id,
                    'product_id': quant.product_id.id,
                    'name': quant.product_id.partner_ref,
                    'product_uom_qty': quant.qty,
                    'product_uom': quant.product_uom_id.id,
                    'picking_type_id': self.picking_type_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                }
            else:
                products[quant.product_id.id]['product_uom_qty'] += quant.qty
        move_obj = self.env['stock.move']
        if not available:
            raise Warning(_('Nothing to move'))
        for data in products.values():
            move_obj.create(data)
        self.action_confirm()
        self.action_assign()
