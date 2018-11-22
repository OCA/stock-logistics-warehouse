# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import UserError


class StockScrapExpiredLine(models.Model):

    _name = 'stock.scrap.expired.line'
    _description = 'Stock Scrap Expired Line'

    product_id = fields.Many2one(
        'product.product',
        'Product',
        required=True,
        readonly=True,
    )
    product_uom_id = fields.Many2one(
        'product.uom',
        'Unit of Measure',
        required=True,
        readonly=True,
    )
    lot_id = fields.Many2one(
        'stock.production.lot',
        'Lot',
        states={'done': [('readonly', True)]},
        required=True,
        readonly=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        'Location',
        required=True,
        readonly=True
    )
    expected_scrap_qty = fields.Float(
        'Expected Quantity',
        default=1.0,
        required=True,
        readonly=True,
    )
    scrap_qty = fields.Float(
        'Quantity',
        default=0.0,
        required=True,
        states={'done': [('readonly', True)]},
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Status',
        default="draft",
        readonly=True,
    )
    stock_scrap_expired_id = fields.Many2one(
        'stock.scrap.expired',
        required=True,
        index=True,
        readonly=True,
        ondelete='cascade',
    )
    stock_scrap_id = fields.Many2one(
        'stock.scrap',
        'Scrap',
        readonly=True
    )
    move_id = fields.Many2one(
        'stock.move',
        'Scrap Move',
        related='stock_scrap_id.move_id',
        readonly=True,
        store=True,
    )

    @api.multi
    def unlink(self):
        if 'done' in self.mapped('state'):
            raise UserError(_('You cannot delete a scrap which is done.'))
        return super(StockScrapExpiredLine, self).unlink()

    @api.multi
    def _prepare_stock_scrap_value(self):
        self.ensure_one()
        return {
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'location_id': self.location_id.id,
            'lot_id': self.lot_id.id,
            'owner_id': self.stock_scrap_expired_id.owner_id.id,
            'scrap_location_id':
                self.stock_scrap_expired_id.scrap_location_id.id,
            'scrap_qty': self.scrap_qty,
            'origin': (self.stock_scrap_expired_id.origin or
                       self.stock_scrap_expired_id.name)
        }

    @api.multi
    def do_scrap(self):
        stock_scrap_obj = self.env['stock.scrap']
        for rec in self:
            val = {
                'state': 'done'
            }
            rounding = rec.product_uom_id.rounding
            if not float_is_zero(rec.scrap_qty, precision_rounding=rounding):
                scrap_value = rec._prepare_stock_scrap_value()
                val['stock_scrap_id'] = stock_scrap_obj.create(scrap_value).id
            rec.write(val)
