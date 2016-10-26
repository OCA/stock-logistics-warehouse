# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class StockDemandEstimate(models.Model):
    _name = 'stock.demand.estimate'
    _description = 'Stock Demand Estimate Line'

    period_id = fields.Many2one(
        comodel_name="stock.demand.estimate.period",
        string="Estimating Period",
        required=True)
    product_id = fields.Many2one(comodel_name="product.product",
                                 string="Product", required=True)
    product_uom = fields.Many2one(comodel_name="product.uom",
                                  string="Unit of measure")
    location_id = fields.Many2one(comodel_name="stock.location",
                                  string="Location", required=True)
    product_uom_qty = fields.Float(
        string="Quantity",
        digits_compute=dp.get_precision('Product Unit of Measure'))
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.demand.estimate'))

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = "%s - %s - %s" % (rec.period_id.name, rec.product_id.name,
                                     rec.location_id.name)
            res.append((rec.id, name))
        return res
