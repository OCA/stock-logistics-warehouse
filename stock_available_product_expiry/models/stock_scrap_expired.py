# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockScrapExpired(models.Model):

    _name = 'stock.scrap.expired'
    _description = 'Stock Scrap Expired'

    def _get_default_scrap_location_id(self):
        return self.env['stock.location'].search(
            [('scrap_location', '=', True)], limit=1).id

    def _get_default_location_id(self):
        return self.env.ref(
            'stock.stock_location_stock', raise_if_not_found=False)

    name = fields.Char(
        'Reference',
        default=lambda self: _('New'),
        copy=False,
        readonly=True,
        required=True,
        states={'done': [('readonly', True)]}
    )
    origin = fields.Char(
        string='Source Document'
    )
    owner_id = fields.Many2one(
        'res.partner',
        'Owner',
        states={'done': [('readonly', True)]}
    )
    location_id = fields.Many2one(
        'stock.location',
        'Location',
        domain="[('usage', '=', 'internal')]",
        required=True,
        states={'done': [('readonly', True)]},
        default=_get_default_location_id)
    scrap_location_id = fields.Many2one(
        'stock.location',
        'Scrap Location',
        default=_get_default_scrap_location_id,
        domain="[('scrap_location', '=', True)]",
        states={'done': [('readonly', True)]}
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('prepared', 'Prepared'),
        ('done', 'Done')],
        string='Status',
        default="draft"
    )
    removal_date = fields.Datetime(
        'Expirity date',
        default=fields.Datetime.now
    )
    stock_scrap_expired_line_ids = fields.One2many(
        'stock.scrap.expired.line',
        inverse_name='stock_scrap_expired_id',
        states={'done': [('readonly', True)]},
    )
    move_ids = fields.One2many(
        'stock.move',
        compute='_compute_move_ids',
        readonly=True,
    )

    @api.depends('state')
    @api.multi
    def _compute_move_ids(self):
        for rec in self:
            rec.move_ids = rec.mapped(
                'stock_scrap_expired_line_ids.move_id')

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.scrap.expired') or _('New')
        scrap = super(StockScrapExpired, self).create(vals)
        return scrap

    @api.multi
    def unlink(self):
        if 'done' in self.mapped('state'):
            raise UserError(_('You cannot delete a scrap which is done.'))
        return super(StockScrapExpired, self).unlink()

    @api.multi
    def _get_expired_quants_domain(self):
        self.ensure_one()
        product_obj = self.env['product.product']
        return product_obj.with_context(
            location=self.location_id.id)._get_expired_quants_domain(
            removal_date=self.removal_date)[0]

    @api.multi
    def _prepare_line_value(self, stock_quant):
        return {
            'product_id': stock_quant.product_id.id,
            'location_id': stock_quant.location_id.id,
            'lot_id': stock_quant.lot_id.id,
            'product_uom_id': stock_quant.product_uom_id.id,
            'expected_scrap_qty': stock_quant.qty,
            'scrap_qty': 0.0,
        }

    @api.onchange('removal_date', 'location_id')
    @api.multi
    def _onchange_removal_date_location_id(self):
        stock_quand_obj = self.env['stock.quant']
        line_obj = self.env['stock.scrap.expired.line']
        for rec in self:
            rec.stock_scrap_expired_line_ids = line_obj.browse([])
            quant_domain = rec._get_expired_quants_domain()
            for quant in stock_quand_obj.search(quant_domain):
                vals = rec._prepare_line_value(quant)
                rec.stock_scrap_expired_line_ids += line_obj.new(vals)
        return {}

    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.stock_scrap_expired_line_ids.do_scrap()
            rec.write({'state': 'done'})

    @api.multi
    def action_get_stock_moves(self):
        action = self.env.ref('stock.stock_move_action').read([])[0]
        action['domain'] = [('id', 'in', self.move_ids.ids)]
        return action
