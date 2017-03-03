# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp

UNIT = dp.get_precision('Product Unit of Measure')


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    @api.multi
    @api.depends('qty', 'reservation_id')
    def _compute_reserved_qty_uom(self):
        uom_obj = self.env['product.uom']
        for rec in self:
            if rec.reservation_id:
                rec.reserved_qty_uom = uom_obj._compute_qty_obj(
                    rec.product_id.uom_id,
                    rec.qty,
                    rec.reservation_id.product_uom)

    reserved_qty_uom = fields.Float(string="Qty in reservation UoM",
                                    compute="_compute_reserved_qty_uom",
                                    help="Quantity expressed in the unit of "
                                         "measure of the move",
                                    digits=UNIT, readonly=True)
    reservation_uom = fields.Many2one(string="Reservation UoM",
                                      comodel_name="product.uom",
                                      readonly=True,
                                      related='reservation_id.product_uom')
