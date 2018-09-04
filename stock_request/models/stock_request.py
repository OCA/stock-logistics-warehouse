# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare

REQUEST_STATES = [
    ('draft', 'Draft'),
    ('open', 'In progress'),
    ('done', 'Done'),
    ('cancel', 'Cancelled')]


class StockRequest(models.Model):
    _name = "stock.request"
    _description = "Stock Request"
    _inherit = 'stock.request.abstract'

    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    name = fields.Char(
        states={'draft': [('readonly', False)]}
    )
    state = fields.Selection(selection=REQUEST_STATES, string='Status',
                             copy=False, default='draft', index=True,
                             readonly=True, track_visibility='onchange',
                             )
    requested_by = fields.Many2one(
        'res.users', 'Requested by', required=True,
        track_visibility='onchange',
        default=lambda s: s._get_default_requested_by(),
    )
    expected_date = fields.Datetime(
        'Expected Date', default=fields.Datetime.now, index=True,
        required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        help="Date when you expect to receive the goods.",
    )
    picking_policy = fields.Selection([
        ('direct', 'Receive each product when available'),
        ('one', 'Receive all products at once')],
        string='Shipping Policy', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default='direct',
    )
    move_ids = fields.One2many(comodel_name='stock.move',
                               compute='_compute_move_ids',
                               string='Stock Moves', readonly=True,
                               )
    picking_ids = fields.One2many('stock.picking',
                                  compute='_compute_picking_ids',
                                  string='Pickings', readonly=True,
                                  )
    qty_in_progress = fields.Float(
        'Qty In Progress', digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, compute='_compute_qty', store=True,
        help="Quantity in progress.",
    )
    qty_done = fields.Float(
        'Qty Done', digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, compute='_compute_qty', store=True,
        help="Quantity completed",
    )
    picking_count = fields.Integer(string='Delivery Orders',
                                   compute='_compute_picking_ids',
                                   readonly=True,
                                   )
    allocation_ids = fields.One2many(comodel_name='stock.request.allocation',
                                     inverse_name='stock_request_id',
                                     string='Stock Request Allocation')
    order_id = fields.Many2one(
        'stock.request.order',
        readonly=True,
    )
    warehouse_id = fields.Many2one(
        states={'draft': [('readonly', False)]}, readonly=True
    )
    location_id = fields.Many2one(
        states={'draft': [('readonly', False)]}, readonly=True
    )
    product_id = fields.Many2one(
        states={'draft': [('readonly', False)]}, readonly=True
    )
    product_uom_id = fields.Many2one(
        states={'draft': [('readonly', False)]}, readonly=True
    )
    product_uom_qty = fields.Float(
        states={'draft': [('readonly', False)]}, readonly=True
    )
    procurement_group_id = fields.Many2one(
        states={'draft': [('readonly', False)]}, readonly=True
    )
    company_id = fields.Many2one(
        states={'draft': [('readonly', False)]}, readonly=True
    )
    route_id = fields.Many2one(
        states={'draft': [('readonly', False)]}, readonly=True
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)',
         'Stock Request name must be unique'),
    ]

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(StockRequest, self).onchange_product_id()
        if self.product_id:
            routes = [r.id for r in self.route_ids]
            res['domain']['route_id'] = "[('id','=',{ids})]".format(ids=tuple(routes))
        return res

    @api.depends('allocation_ids')
    def _compute_move_ids(self):
        for request in self.sudo():
            request.move_ids = request.allocation_ids.mapped('stock_move_id')

    @api.depends('allocation_ids')
    def _compute_picking_ids(self):
        for request in self.sudo():
            request.picking_count = 0
            request.picking_ids = self.env['stock.picking']
            request.picking_ids = request.move_ids.filtered(
                lambda m: m.state != 'cancel').mapped('picking_id')
            request.picking_count = len(request.picking_ids)

    @api.depends(
        'allocation_ids',
        'allocation_ids.stock_move_id.state',
    )
    def _compute_qty(self):
        for request in self.sudo():
            done_qty = sum(request.allocation_ids.mapped(
                'allocated_product_qty'))
            open_qty = sum(request.allocation_ids.mapped('open_product_qty'))
            request.qty_done = request.product_id.uom_id._compute_quantity(
                done_qty, request.product_uom_id)
            request.qty_in_progress = \
                request.product_id.uom_id._compute_quantity(
                    open_qty, request.product_uom_id)

    @api.constrains('order_id', 'requested_by')
    def check_order_requested_by(self):
        if self.order_id and self.order_id.requested_by != self.requested_by:
            raise ValidationError(_(
                'Requested by must be equal to the order'
            ))

    @api.constrains('order_id', 'warehouse_id')
    def check_order_warehouse_id(self):
        if self.order_id and self.order_id.warehouse_id != self.warehouse_id:
            raise ValidationError(_(
                'Warehouse must be equal to the order'
            ))

    @api.constrains('order_id', 'location_id')
    def check_order_location(self):
        if self.order_id and self.order_id.location_id != self.location_id:
            raise ValidationError(_(
                'Location must be equal to the order'
            ))

    @api.constrains('order_id', 'procurement_group_id')
    def check_order_procurement_group(self):
        if (
            self.order_id and
            self.order_id.procurement_group_id != self.procurement_group_id
        ):
            raise ValidationError(_(
                'Procurement group must be equal to the order'
            ))

    @api.constrains('order_id', 'company_id')
    def check_order_company(self):
        if self.order_id and self.order_id.company_id != self.company_id:
            raise ValidationError(_(
                'Company must be equal to the order'
            ))

    @api.constrains('order_id', 'expected_date')
    def check_order_expected_date(self):
        if self.order_id and self.order_id.expected_date != self.expected_date:
            raise ValidationError(_(
                'Expected date must be equal to the order'
            ))

    @api.constrains('order_id', 'picking_policy')
    def check_order_picking_policy(self):
        if (
            self.order_id and
            self.order_id.picking_policy != self.picking_policy
        ):
            raise ValidationError(_(
                'The picking policy must be equal to the order'
            ))

    @api.multi
    def _action_confirm(self):
        self._action_launch_procurement_rule()
        self.state = 'open'

    @api.multi
    def action_confirm(self):
        self._action_confirm()
        return True

    def action_draft(self):
        self.state = 'draft'
        return True

    def action_cancel(self):
        self.sudo().mapped('move_ids').action_cancel()
        self.state = 'cancel'
        return True

    def action_done(self):
        self.state = 'done'
        if self.order_id:
            self.order_id.check_done()
        return True

    def check_done(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for request in self:
            allocated_qty = sum(request.allocation_ids.mapped(
                'allocated_product_qty'))
            qty_done = request.product_id.uom_id._compute_quantity(
                allocated_qty, request.product_uom_id)
            if float_compare(qty_done, request.product_uom_qty,
                             precision_digits=precision) >= 0:
                request.action_done()
        return True

    def _prepare_procurement_values(self, group_id=False):

        """ Prepare specific key for moves or other components that
        will be created from a procurement rule
        coming from a stock request. This method could be override
        in order to add other custom key that could be used in
        move/po creation.
        """
        return {

            'name': self.name,
            'origin': self.name,
            'company_id': self.company_id.id,
            'date_planned': self.expected_date,
            'product_id': self.product_id.id,
            'product_qty': self.product_uom_qty,
            'product_uom': self.product_uom_id.id,
            'location_id': self.location_id.id,
            'warehouse_id': self.warehouse_id.id,
            'stock_request_allocation_ids': [(4, self.id)],
            'group_id': group_id or self.procurement_group_id.id or False,
            'route_ids': [(4, self.route_id.id)],
            'stock_request_id': self.id,
        }

    @api.multi
    def _action_launch_procurement_rule(self):
        """
        Launch procurement group run method with required/custom
        fields genrated by a
        stock request. procurement group will launch '_run_move',
        '_run_buy' or '_run_manufacture'
        depending on the stock request product rule.
        """
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for request in self:
            if (
                request.state != 'draft' or
                request.product_id.type not in ('consu', 'product')
            ):
                continue
            qty = 0.0
            for move in request.move_ids.filtered(
                    lambda r: r.state != 'cancel'):
                qty += move.product_qty

            if float_compare(qty, request.product_qty,
                             precision_digits=precision) >= 0:
                continue

            values = request._prepare_procurement_values(
                group_id=request.procurement_group_id)

            procurement = self.env["procurement.order"].create(values)
            if procurement:
                procurement.run()
        return True

    @api.multi
    def action_view_transfer(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [
                (self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action

    @api.model
    def create(self, vals):
        upd_vals = vals.copy()
        if upd_vals.get('name', '/') == '/':
            upd_vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.request')
        return super(StockRequest, self).create(upd_vals)

    @api.multi
    def unlink(self):
        if self.filtered(lambda r: r.state != 'draft'):
            raise UserError(_('Only requests on draft state can be unlinked'))
        return super(StockRequest, self).unlink()
