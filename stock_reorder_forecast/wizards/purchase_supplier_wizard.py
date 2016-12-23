# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime
from openerp import api, fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF


class PurchaseSupplierWizard(models.TransientModel):

    _name = "purchase.purchase_supplier_wizard"
    _description = "wizard create proposal purchase from supplier"

    @api.model
    def default_get(self, fields_list):
        """At start partner_id is to be taken from active_id,
        later defaults are
        retained in the wizard record.
        """
        result = {}
        result = super(PurchaseSupplierWizard, self).default_get(
            fields_list=fields_list
        )
        partner_model = self.env['res.partner']
        partner_ids = self.env.context.get("active_ids", False)
        if partner_ids:
            partner = partner_model.browse(partner_ids[0])
            products = partner.product_ids
            if products:
                result['supplier_products'] = partner.product_ids.ids
                result[
                    'supplier_products_primary'
                    ] = partner.primary_product_ids.ids
                result["name"] = partner.id
                result["stock_period_min"] = partner.stock_period_min
                result["stock_period_max"] = partner.stock_period_max
                today = date.today().strftime(DSDF)
                result['ultimate_purchase'] = partner.ultimate_purchase
                pending_rfqs = self.env['purchase.order'].search(
                    [("partner_id", '=', partner.id),
                     ("state", 'in', ['draft', 'sent'])]
                ).ids
                purchase_order_ids = self.env['purchase.order'].search(
                    [('partner_id', '=', partner.id)]).ids
                result['pending_rfq_lines'] = self.env[
                    'purchase.order.line'].search(
                        [('order_id', 'in', pending_rfqs),
                         ('order_id', 'in', purchase_order_ids)]).ids
                if partner.ultimate_purchase < today:
                    result["ultimate_purchase_to"] = today
        # TODO CHECK RFQ/PO MANAGMENT FROM PARTNER.
        return result

    def _get_qty(self, prd_tmpl, supplier, stock_period_max):
        product = self.env['product.product'].search(
            [('product_tmpl_id', '=', prd_tmpl.id)], limit=1)
        qty = self.env['purchase.purchase_wizard']._get_qty(
            product, supplier, stock_period_max)
        return qty

    @api.multi
    def create_partner_rfq(self):
        po_model = self.env["purchase.order"]
        date_order = date.today().strftime(DSDF)
        supplier_id = int(self.name)
        order_vals = {
            "partner_id": supplier_id,
            "origin": "purchase proposal",
            "date_order": date_order, }
        purchase_order = po_model.create(order_vals)
        products = self.supplier_products
        if self.primary_supplier_only:
            products = self.supplier_products_primary
        for product in products:
            supplier = product.seller_ids.filtered(
                lambda x: x.name.id == supplier_id
            )
            pol_model = self.env["purchase.order.line"]
            qty = self._get_qty(product, supplier, self.stock_period_max)
            if qty > 0:
                line_vals = {
                    'name': 'Batch resupply of product %s from partner %s '
                            % (product.name, supplier.name.name),
                    'product_id': product.id,
                    'product_uom': product.uom_id.id,
                    'product_qty': qty,
                    'order_id': purchase_order.id,
                    'date_planned':
                        self.ultimate_purchase_to or datetime.today(),
                    'price_unit': supplier.price
                }
                pol = pol_model.create(line_vals)
                pol._compute_amount()
                # ZERO IN  ULTIMATE PURCHASE WHEN  WRITE DONE
                product.write({"ultimate_purchase": False})
        return purchase_order

    name = fields.Many2one(
        comodel_name="res.partner",
        string='Supplier name'
    )
    supplier_products = fields.Many2many(
        "product.template",
        string="Products supplied by this partner"
    )
    supplier_products_primary = fields.Many2many(
        "product.template",
        string="Products supplied by this partner as primary",
    )
    ultimate_purchase = fields.Date("ultimate purchase")
    pending_rfq_lines = fields.Many2many("purchase.order.line")
    stock_period_min = fields.Integer(
        string="Delivery period",
        readonly="1",
        help="""Minimum stock for this supplier in days."""
    )
    stock_period_max = fields.Integer(
        string="Maximum stock",
        help="Default period for this supplier in days to resupply for."
    )
    primary_supplier_only = fields.Boolean(
        string="Primary only",
        default=False,
        help="""If selected will create orders only for products where this
        vendor is primary supplier, a vendor is considered primary if he is the
         first vendor of the vendor list"""
    )
    ultimate_purchase_to = fields.Date(
        string="Date Planned"
    )
