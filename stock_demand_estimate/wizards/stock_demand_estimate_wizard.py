# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class StockDemandEstimateSheet(models.TransientModel):
    _name = 'stock.demand.estimate.sheet'
    _description = 'Stock Demand Estimate Sheet'

    def _default_estimate_ids(self):
        date_start = self.env.context.get('default_date_start', False)
        date_end = self.env.context.get('default_date_end', False)
        date_range_type_id = self.env.context.get('default_date_range_type_id',
                                                  False)
        location_id = self.env.context.get('default_location_id', False)
        product_ids = self.env.context.get('product_ids', False)
        domain = [('type_id', '=', date_range_type_id), '|', '&',
                  ('date_start', '>=', date_start),
                  ('date_start', '<=', date_end),
                  '&',
                  ('date_end', '>=', date_start),
                  ('date_end', '<=', date_end)]
        periods = self.env['date.range'].search(
            domain)
        domain = [('type_id', '=', date_range_type_id),
                  ('date_start', '<=', date_start),
                  ('date_end', '>=', date_start)]
        periods |= self.env['date.range'].search(
            domain)
        products = self.env['product.product'].browse(product_ids)

        lines = []
        for product in products:
            name_y = ''
            if product.default_code:
                name_y += '[%s] ' % product.default_code
            name_y += product.name
            name_y += ' - %s' % product.uom_id.name
            for period in periods:
                estimates = self.env['stock.demand.estimate'].search(
                    [('product_id', '=', product.id),
                     ('date_range_id', '=', period.id),
                     ('location_id', '=', location_id)])
                if estimates:
                    lines.append((0, 0, {
                        'value_x': period.name,
                        'value_y': name_y,
                        'date_range_id': period.id,
                        'product_id': product.id,
                        'product_uom': estimates[0].product_uom.id,
                        'location_id': location_id,
                        'estimate_id': estimates[0].id,
                        'product_uom_qty': estimates[0].product_uom_qty
                    }))
                else:
                    lines.append((0, 0, {
                        'value_x': period.name,
                        'value_y': name_y,
                        'date_range_id': period.id,
                        'product_id': product.id,
                        'product_uom': product.uom_id.id,
                        'location_id': location_id,
                        'product_uom_qty': 0.0
                    }))
        return lines

    date_start = fields.Date(string="Date From", readonly=True)
    date_end = fields.Date(string="Date From", readonly=True)
    date_range_type_id = fields.Many2one(string='Date Range Type',
                                         comodel_name='date.range.type',
                                         readonly=True)
    location_id = fields.Many2one(comodel_name="stock.location",
                                  string="Location", readonly=True)
    line_ids = fields.Many2many(
        string="Estimates",
        comodel_name='stock.demand.estimate.sheet.line',
        relation='stock_demand_estimate_line_rel',
        default=_default_estimate_ids)

    @api.model
    def _prepare_estimate_data(self, line):
        return {
            'date_range_id': line.date_range_id.id,
            'product_id': line.product_id.id,
            'location_id': line.location_id.id,
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_id.uom_id.id,
        }

    @api.multi
    def button_validate(self):
        res = []
        for line in self.line_ids:
            if line.estimate_id:
                line.estimate_id.product_uom_qty = line.product_uom_qty
                res.append(line.estimate_id.id)
            else:
                data = self._prepare_estimate_data(line)
                estimate = self.env['stock.demand.estimate'].create(
                    data)
                res.append(estimate.id)
        res = {
            'domain': [('id', 'in', res)],
            'name': _('Stock Demand Estimates'),
            'src_model': 'stock.demand.estimate.wizard',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'stock.demand.estimate',
            'type': 'ir.actions.act_window'
        }
        return res


class StockDemandEstimateSheetLine(models.TransientModel):
    _name = 'stock.demand.estimate.sheet.line'
    _description = 'Stock Demand Estimate Sheet Line'

    estimate_id = fields.Many2one(comodel_name='stock.demand.estimate')
    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Period')
    location_id = fields.Many2one(comodel_name='stock.location',
                                  string="Stock Location")
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product')
    value_x = fields.Char(string='Period')
    value_y = fields.Char(string='Product')
    product_uom_qty = fields.Float(
        string="Quantity", digits=dp.get_precision('Product UoM'))


class DemandEstimateWizard(models.TransientModel):
    _name = 'stock.demand.estimate.wizard'
    _description = 'Stock Demand Estimate Wizard'

    date_start = fields.Date(string="Date From", required=True)
    date_end = fields.Date(string="Date To", required=True)
    date_range_type_id = fields.Many2one(string='Date Range Type',
                                         comodel_name='date.range.type',
                                         required=True)
    location_id = fields.Many2one(comodel_name="stock.location",
                                  string="Location", required=True)
    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products")

    @api.onchange('date_range_type_id')
    def _onchange_date_range_type_id(self):
        if self.date_range_type_id.company_id:
            return {
                'domain': {
                    'location_id': [('company_id', '=',
                                     self.date_range_type_id.company_id.id)]}}
        return {}

    @api.constrains('date_start', 'date_end')
    def _check_start_end_dates(self):
        for rec in self:
            if rec.date_start > rec.date_end:
                raise ValidationError(_(
                    'The start date cannot be later than the end date.'))

    @api.multi
    def _prepare_demand_estimate_sheet(self):
        self.ensure_one()
        return {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'date_range_type_id': self.date_range_type_id.id,
            'location_id': self.location_id.id,
        }

    @api.multi
    def create_sheet(self):
        self.ensure_one()
        if not self.product_ids:
            raise UserError(_('You must select at least one product.'))

        context = {
            'default_date_start': self.date_start,
            'default_date_end': self.date_end,
            'default_date_range_type_id': self.date_range_type_id.id,
            'default_location_id': self.location_id.id,
            'product_ids': self.product_ids.ids
        }
        res = {
            'context': context,
            'name': _('Estimate Sheet'),
            'src_model': 'stock.demand.estimate.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'stock.demand.estimate.sheet',
            'type': 'ir.actions.act_window'
        }

        return res
