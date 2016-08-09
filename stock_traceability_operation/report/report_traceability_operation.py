# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields
from openerp.addons import decimal_precision as dp


class ReportStockTraceabilityOperation(models.TransientModel):
    _name = 'report.stock.traceability_operation'
    _description = "Detailed traceability"
    _order = 'date, move_id, operation_id'

    name = fields.Char('Move description')
    move_id = fields.Many2one(
        'stock.move', 'Stock Move',
        help="The stock move on which this part of the traceability is based")
    operation_id = fields.Many2one(
        'stock.pack.operation', 'Pack Operation',
        help="The operation on which this part of the "
             "traceability is based. When this field is empty, this part of "
             "the traceability is directly based on the Stock Move.")
    picking_id = fields.Many2one('stock.picking', 'Reference')
    origin = fields.Char('Source')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type')
    create_date = fields.Datetime('Creation Date')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom_qty = fields.Float(
        'Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        help="This is the quantity of products moved in this Stock Move or "
             "in this Pack Operation")
    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure',
        help="The unit of measure of the product")
    product_uos_qty = fields.Float(
        'Quantity (UOS)',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uos = fields.Many2one('product.uom', 'Product UOS')
    location_id = fields.Many2one('stock.location', 'Source Location')
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location')
    date = fields.Datetime('Date')
    date_expected = fields.Datetime('Expected Date')
    state = fields.Selection(
        [('draft', 'New'),
         ('cancel', 'Cancelled'),
         ('waiting', 'Waiting Another Move'),
         ('confirmed', 'Waiting Availability'),
         ('assigned', 'Available'),
         ('done', 'Done')],
        'Status')
    partner_id = fields.Many2one('res.partner', 'Destination Address')
