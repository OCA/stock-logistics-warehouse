# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class ProductStockLocation(models.Model):
    _name = 'product.stock.location'
    _description = "Product Stock Location"

    @api.multi
    @api.depends('quant_ids',
                 'quant_ids.location_id',
                 'quant_ids.product_id',
                 'quant_ids.qty',
                 'quant_ids.reservation_id',
                 'incoming_move_ids',
                 'incoming_move_ids.product_id',
                 'incoming_move_ids.location_dest_id',
                 'incoming_move_ids.state',
                 'incoming_move_ids.product_uom_qty',
                 'outgoing_move_ids',
                 'outgoing_move_ids.product_id',
                 'outgoing_move_ids.location_id',
                 'outgoing_move_ids.product_uom_qty',
                 'child_ids',
                 'child_ids.location_id',
                 'child_ids.parent_id',
                 'child_ids.quant_ids',
                 'child_ids.incoming_move_ids',
                 'child_ids.outgoing_move_ids',
                 'child_ids.product_location_qty',
                 'child_ids.incoming_location_qty',
                 'child_ids.outgoing_location_qty',
                 'child_ids.virtual_location_qty')
    def _compute_product_available_qty(self):
        for rec in self:
            product_available = rec.product_id.with_context(
                location=rec.location_id.id)._product_available()[
                rec.product_id.id]
            rec.product_location_qty = product_available['qty_available']
            rec.incoming_location_qty = product_available['incoming_qty']
            rec.outgoing_location_qty = product_available['outgoing_qty']
            rec.virtual_location_qty = product_available['virtual_available']

    @api.multi
    @api.depends('product_id', 'location_id')
    def _compute_orderpoint_id(self):
        for rec in self:
            orderpoints = self.env['stock.warehouse.orderpoint'].search(
                [('product_id', '=', rec.product_id.id),
                 ('location_id', '=', rec.location_id.id)])
            if orderpoints:
                rec.orderpoint_id = orderpoints[0]

    @api.multi
    @api.depends('product_id', 'location_id')
    def _compute_name(self):
        for rec in self:
            name = '%s: ' % rec.location_id.complete_name
            if rec.product_id.default_code:
                name += '[%s] ' % rec.product_id.default_code
            name += '%s' % rec.product_id.name
            rec.name = name

    name = fields.Char(string="Name", compute="_compute_name")
    product_id = fields.Many2one(comodel_name='product.product',
                                 string="Product",
                                 ondelete='cascade',
                                 required=True)
    location_id = fields.Many2one(comodel_name='stock.location',
                                  string='Stock Location',
                                  ondelete='cascade',
                                  required=True)
    parent_id = fields.Many2one(comodel_name='product.stock.location',
                                string="Parent Product Stock Location")
    child_ids = fields.One2many(comodel_name='product.stock.location',
                                inverse_name='parent_id')
    quant_ids = fields.One2many(comodel_name='stock.quant',
                                inverse_name='product_stock_location_id',
                                string="Stock Quants")
    incoming_move_ids = fields.One2many(
        comodel_name='stock.move',
        inverse_name='product_stock_location_dest_id',
        string="Incoming moves")
    outgoing_move_ids = fields.One2many(
        comodel_name='stock.move',
        inverse_name='product_stock_location_id',
        string="Outgoing moves")

    product_location_qty = fields.Float(
        string='Quantity On Location',
        compute='_compute_product_available_qty',
        store=True)
    incoming_location_qty = fields.Float(
        string='Incoming On Location',
        compute='_compute_product_available_qty',
        store=True)
    outgoing_location_qty = fields.Float(
        string='Outgoing On Location',
        compute='_compute_product_available_qty',
        store=True)
    virtual_location_qty = fields.Float(
        string='Forecast On Location',
        compute='_compute_product_available_qty',
        store=True)
    company_id = fields.Many2one(comodel_name='res.company',
                                 related='location_id.company_id',
                                 store=True)
    orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Orderpoint",
        compute='_compute_orderpoint_id', store=True)

    _sql_constraints = [
        ('uniq_product_location',
         'unique(product_id, location_id)',
         'Product and Location already defined'),
    ]

    @api.model
    def search_children_product_stock_location_domain(self, location):
        return [('product_id', '=', self.product_id.id),
                ('location_id.location_id', '=', location.id),
                '|', ('parent_id', '=', False),
                ('parent_id.location_id', '!=', location.id)]

    @api.model
    def search_parent_product_stock_location_domain(self, location):
        return [('product_id', '=', self.product_id.id),
                ('location_id', '=', location.location_id.id)]

    @api.model
    def update_children(self):
        for rec in self:
            for child in rec.child_ids:
                child.parent_id = False
        for psl in self.search(
                self.search_children_product_stock_location_domain(
                    self.location_id)):
            psl.parent_id = self

    @api.model
    def prepare_parent_product_stock_location_data(self):
        return {
            'product_id': self.product_id.id,
            'location_id': self.location_id.location_id.id,
        }

    @api.model
    def update_parent(self):
        pst_model = self.env['product.stock.location']
        if self.location_id.location_id:
            parent_psts = pst_model.search(
                self.search_parent_product_stock_location_domain(
                    self.location_id))
            if not parent_psts:
                pst_model.create(
                    self.prepare_parent_product_stock_location_data())

    @api.model
    def create(self, vals):
        rec = super(ProductStockLocation, self).create(vals)
        rec.sudo().update_children()
        rec.sudo().update_parent()
        return rec

    @api.multi
    def write(self, vals):
        if vals.get('location_id', False) and not vals.get('parent_id', False):
            for rec in self:
                rec.parent_id = False
        res = super(ProductStockLocation, self).write(vals)
        if vals.get('location_id', False):
            for rec in self:
                rec.sudo().update_children()
                rec.sudo().update_parent()
        return res
