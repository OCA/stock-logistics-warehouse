# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _default_product_purchase_uom_id(self):
        return self.env.ref('product.product_uom_unit')

    product_tmpl_id = fields.Many2one(
        related='product_id.product_tmpl_id',
        comodel_name='product.template'
    )
    packaging_id = fields.Many2one(
        'product.packaging',
        'Packaging'
    )
    product_purchase_qty = fields.Float(
        'Purchase quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=lambda *a: 1.0
    )
    product_purchase_uom_id = fields.Many2one(
        'product.uom',
        'Purchase Unit of Measure',
        required=True,
        default=_default_product_purchase_uom_id
    )
    product_qty = fields.Float(
        compute="_compute_product_qty",
        string='Quantity',
        inverse='_inverse_product_qty'
    )

    @api.multi
    def _get_product_seller(self):
        self.ensure_one()
        return self.product_id._select_seller(
            partner_id=self.order_id.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and
            fields.Date.from_string(self.order_id.date_order),
            uom_id=self.product_uom)

    @api.multi
    @api.depends('product_purchase_uom_id', 'product_purchase_qty')
    def _compute_product_qty(self):
        """
        Compute the total quantity
        """
        for line in self:
            uom_obj = self.env['product.uom']
            to_uom = uom_obj.search(
                [('category_id',
                  '=',
                  line.product_purchase_uom_id.category_id.id),
                 ('uom_type', '=', 'reference')], limit=1)
            if not line.product_purchase_uom_id:
                return
            line.product_qty = line.product_purchase_uom_id._compute_quantity(
                line.product_purchase_qty,
                to_uom)

    @api.multi
    def _inverse_product_qty(self):
        """ If product_quantity is set compute the purchase_qty
        """
        for line in self:
            if line.product_id:
                supplier = line._get_product_seller()
                if supplier:
                    product_purchase_uom = supplier.min_qty_uom_id
                    uom_obj = self.env['product.uom']
                    from_uom = uom_obj.search(
                        [('category_id', '=',
                          product_purchase_uom.category_id.id),
                         ('uom_type', '=', 'reference')], limit=1)
                    line.product_purchase_qty = from_uom._compute_quantity(
                        line.product_qty,
                        product_purchase_uom)
                    line.product_purchase_uom_id = product_purchase_uom.id
            else:
                line.product_purchase_qty = line.product_qty

    @api.onchange("packaging_id")
    def _onchange_packaging_id(self):
        if self.packaging_id:
            self.product_uom = self.packaging_id.uom_id

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ set domain on product_purchase_uom_id and packaging_id
            set the first packagigng, purchase_uom and purchase_qty
        """
        domain = {}
        # call default implementation
        # restore default values
        defaults = self.default_get(
            ['packaging_id', 'product_purchase_uom_id'])
        self.packaging_id = self.packaging_id.browse(
            defaults.get('packaging_id', []))
        self.product_purchase_uom_id = self.product_purchase_uom_id.browse(
            defaults.get('product_purchase_uom_id', []))
        # add default domains
        if self.product_id and self.partner_id:
            domain['packaging_id'] = [
                ('id', 'in', self.product_id.mapped(
                    'seller_ids.packaging_id.id'))]
            domain['product_purchase_uom_id'] = \
                [('id', 'in', self.product_id.mapped(
                    'seller_ids.min_qty_uom_id.id'))]
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            supplier = self._get_product_seller()
        else:
            supplier = self.product_id.seller_ids.browse([])
        if supplier.product_uom:
            # use the uom from the suppleir
            self.product_uom = supplier.product_uom
        if supplier.min_qty_uom_id:
            # if the supplier requires some min qty/uom,
            self.product_purchase_qty = supplier.min_qty
            self.product_purchase_uom_id = supplier.min_qty_uom_id
            domain['product_purchase_uom_id'] = \
                [('id', '=', supplier.min_qty_uom_id.id)]
            to_uom = self.env['product.uom'].search([
                ('category_id', '=',
                 supplier.min_qty_uom_id.category_id.id),
                ('uom_type', '=', 'reference')], limit=1)
            to_uom = to_uom and to_uom[0]
            self.product_qty = supplier.min_qty_uom_id._compute_quantity(
                supplier.min_qty, to_uom
            )
        self.packaging_id = supplier.packaging_id
        if domain:
            if res.get('domain'):
                res['domain'].update(domain)
            else:
                res['domain'] = domain  # pragma: no cover not aware of super
        return res

    @api.multi
    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        val = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for v in val:
            v['product_packaging'] = self.packaging_id.id
        return val

    @api.model
    def update_vals(self, vals):
        """
        When packaging_id is set, uom_id is readonly,
        so we need to reset the uom value in the vals dict
        """
        if vals.get('packaging_id'):
            vals['product_uom'] = self.env['product.packaging'].browse(
                vals['packaging_id']).uom_id.id
        return vals

    @api.model
    @api.returns('self', lambda rec: rec.id)
    def create(self, vals):
        if 'product_qty' not in vals and 'product_purchase_qty' in vals:
            # compute product_qty to avoid inverse computation and reset to 1
            uom_obj = self.env['product.uom']
            product_purchase_uom = uom_obj.browse(
                vals['product_purchase_uom_id'])
            to_uom = uom_obj.search(
                [('category_id', '=', product_purchase_uom.category_id.id),
                 ('uom_type', '=', 'reference')], limit=1)
            vals['product_qty'] = to_uom._compute_quantity(
                vals['product_purchase_qty'],
                to_uom)
        return super(PurchaseOrderLine, self).create(self.update_vals(vals))

    @api.multi
    def write(self, vals):
        return super(PurchaseOrderLine, self).write(self.update_vals(vals))
