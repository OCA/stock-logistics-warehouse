# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.cr_uid_context
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id,
                                 group_id, context=None):
        """ Set product_packaging on stock move
        """
        result = super(PurchaseOrder, self)._prepare_order_line_move(
            cr, uid, order, order_line, picking_id, group_id,
            context=context)
        if order_line.packaging_id:
            for res in result:
                res['product_packaging'] = order_line.packaging_id.id
        return result


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _default_product_purchase_uom_id(self):
        return self.env.ref('product.product_uom_unit')

    product_tmpl_id = fields.Many2one(related='product_id.product_tmpl_id',
                                      comodel_name='product.template')
    packaging_id = fields.Many2one('product.packaging', 'Packaging')
    product_purchase_qty = fields.Float(
        'Purchase quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True, default=lambda *a: 1.0)
    product_purchase_uom_id = fields.Many2one(
        'product.uom', 'Purchase Unit of Measure', required=True,
        default=_default_product_purchase_uom_id)
    product_qty = fields.Float(
        compute="_compute_product_qty", string='Quantity',
        inverse='_inverse_product_qty',)

    @api.one
    @api.depends('product_purchase_uom_id', 'product_purchase_qty')
    def _compute_product_qty(self):
        """
        Compute the total quantity
        """
        uom_obj = self.env['product.uom']
        to_uom = uom_obj.search(
            [('category_id', '=', self.product_purchase_uom_id.category_id.id),
             ('uom_type', '=', 'reference')], limit=1)
        self.product_qty = uom_obj._compute_qty(
            self.product_purchase_uom_id.id,
            self.product_purchase_qty,
            to_uom.id)

    @api.one
    def _inverse_product_qty(self):
        """ If product_quantity is set compute the purchase_qty
        """
        if self.product_id and self.order_id.partner_id:
            for supplier in self.product_id.seller_ids:
                if (supplier.name.id == self.order_id.partner_id.id):
                    product_purchase_uom = supplier.min_qty_uom_id
                    uom_obj = self.env['product.uom']
                    from_uom = uom_obj.search(
                        [('category_id', '=',
                          product_purchase_uom.category_id.id),
                         ('uom_type', '=', 'reference')], limit=1)
                    self.product_purchase_qty = uom_obj._compute_qty(
                        from_uom.id,
                        self.product_qty,
                        product_purchase_uom.id,)
                    self.product_purchase_uom_id = product_purchase_uom.id
                    break
        else:
            self.product_purchase_qty = self.product_qty

    @api.onchange("packaging_id")
    def _onchange_packaging_id(self):
        if self.packaging_id:
            self.product_uom = self.packaging_id.uom_id

    @api.cr_uid_context
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty,
                            uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft',
                            context=None):
        """ set domain on product_purchase_uom_id and packaging_id
            if there is no qty (first pass),
            set the first packagigng, purchase_uom and purchase_qty
        """
        product_product = self.pool['product.product']
        product_purchase_qty = 0
        product_purchase_uom_id = False
        category_product_purchase_uom_id = False
        packaging_id = False
        new_uom_id = False
        domain = {}

        if product_id and partner_id:
            product = product_product.browse(cr, uid, product_id,
                                             context=context)
            first = True
            packaging_ids = []
            po_uom_ids = []
            domain['packaging_id'] = [('id', 'in', packaging_ids)]
            domain['product_purchase_uom_id'] = [('id', 'in', po_uom_ids)]
            for supplier in product.seller_ids:
                if (supplier.name.id == partner_id):
                    if first:
                        product_purchase_qty = supplier.min_qty
                        product_purchase_uom_id = supplier.min_qty_uom_id.id
                        category_product_purchase_uom_id = \
                            supplier.min_qty_uom_id.category_id.id
                        new_uom_id = supplier.product_uom.id
                        if supplier.packaging_id:
                            packaging_id = supplier.packaging_id.id
                        first = False
                    po_uom_ids.append(supplier.min_qty_uom_id.id)
                    if supplier.packaging_id:
                        packaging_ids.append(supplier.packaging_id.id)

        uom_id = new_uom_id if not qty else uom_id
        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order,
            fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, state=state, context=context)

        if not qty:
            res['value']['product_purchase_qty'] = product_purchase_qty
            res['value']['product_purchase_uom_id'] = product_purchase_uom_id
            uom_obj = self.pool['product.uom']
            to_uom_id = uom_obj.search(
                cr, uid,
                [('category_id', '=', category_product_purchase_uom_id),
                 ('uom_type', '=', 'reference')], limit=1, context=context)[0]
            res['value']['product_qty'] = uom_obj._compute_qty(
                cr, uid, product_purchase_uom_id,
                product_purchase_qty, to_uom_id)
            res['value']['packaging_id'] = packaging_id
        if domain:
            if res.get('domain'):
                res['domain'].update(domain)
            else:
                res['domain'] = domain
        return res

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
    def create(self, vals):
        return super(PurchaseOrderLine, self).create(self.update_vals(vals))

    @api.multi
    def write(self, vals):
        return super(PurchaseOrderLine, self).write(self.update_vals(vals))


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _get_po_line_values_from_proc(self, procurement, partner, company,
                                      schedule_date):
        """ add packaging and update product_uom/quantity if necessary
        """
        res = super(ProcurementOrder, self)._get_po_line_values_from_proc(
            procurement, partner, company, schedule_date)

        uom_obj = self.env['product.uom']

        for supplier in procurement.product_id.seller_ids:
            if (supplier.name.id == partner.id):
                if supplier.packaging_id:
                    res['packaging_id'] = supplier.packaging_id.id
                    new_uom_id = supplier.product_uom.id
                    if new_uom_id != res['product_uom']:
                        res['product_uom'] = new_uom_id
                        qty = uom_obj._compute_qty(procurement.product_uom.id,
                                                   procurement.product_qty,
                                                   new_uom_id)
                        res['product_qty'] = max(qty, supplier.qty)
                    break

        return res
