# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class StockOrderpointDemandEstimate(models.Model):
    _name = 'stock.orderpoint.demand.estimate'
    _description = 'Stock orderpoint Demand Estimate Line'

    period_id = fields.Many2one(
        comodel_name="stock.orderpoint.demand.estimate.period",
        string="Estimating Period",
        required=True)
    orderpoint_id = fields.Many2one(comodel_name="stock.warehouse.orderpoint",
                                string="Stock orderpoint")
    product_id = fields.Many2one(comodel_name="product.product",
                                 string="Product",
                                 related="orderpoint_id.product_id")
    product_uom = fields.Many2one(comodel_name="product.uom",
                                  string="Product",
                                  related="orderpoint_id.product_uom")
    location_id = fields.Many2one(comodel_name="stock.location",
                                  string="Location",
                                  related="orderpoint_id.location_id")
    warehouse_id = fields.Many2one(comodel_name="stock.warehouse",
                                   string="Warehouse",
                                   related="orderpoint_id.warehouse_id")
    product_uom_qty = fields.Float(
        string="Quantity",
        digits_compute=dp.get_precision('Product Unit of Measure'))
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.orderpoint.demand.estimate'))

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = "%s - %s" % (rec.period_id.name, rec.orderpoint_id.name)
            res.append((rec.id, name))
        return res
