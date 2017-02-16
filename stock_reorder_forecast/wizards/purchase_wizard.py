# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime
from openerp import api, fields, models
from openerp.tools import float_round
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF


class PurchaseWizard(models.TransientModel):

    _name = "purchase.purchase_wizard"
    _description = "wizard create proposal purchase"

    @api.model
    def default_get(self, fields_list):
        """At start partner_id is to be taken from active_id,
        later defaults are
        retained in the wizard record.
        """
        result = {}
        result = super(PurchaseWizard, self).default_get(
            fields_list=fields_list
        )
        product_model = self.env['product.product']
        product_ids = self.env.context.get("active_ids", False)
        if product_ids:
            product = product_model.browse(product_ids[0])
            supplier = product.product_tmpl_id.seller_ids[0]
            result["product"] = product.id
            if supplier:
                partner = supplier.name
                result["supplier"] = supplier.id
                result["name"] = partner.name
                result["stock_period_min"] = partner.stock_period_min
                result["stock_period_max"] = partner.stock_period_max
                result["stock_avl"] = product.virtual_available
                today = date.today().strftime(DSDF)
                result['ultimate_purchase'] = product.ultimate_purchase
                pending_rfqs = self.env['purchase.order'].search(
                    [("partner_id", '=', supplier.name.id),
                     ("state", 'in', ['draft', 'sent'])]
                ).ids
                result['pending_rfq_lines'] = self.env[
                    'purchase.order.line'].search(
                        [('order_id', 'in', pending_rfqs),
                         ('product_id', '=', product.id)]).ids
                if partner.ultimate_purchase < today:
                    result["ultimate_purchase_to"] = today
        # TODO CHECK RFQ/PO MANAGMENT FROM PARTNER.
        return result

    def _get_qty(self, product, supplier, stock_period_max):
        qty = float_round(
            product.turnover_average * product.stock_period_max -
            product.virtual_available, 0)
        purchase_multiple = supplier.purchase_multiple
        if purchase_multiple == 0:
            purchase_multiple = 1
        qty = int((qty + purchase_multiple - 1) / purchase_multiple)
        qty = qty * purchase_multiple
        if qty < 0:
            qty = 0
        return qty

    @api.multi
    def create_rfq(self):
        # check if there is a PO request already with this product and this
        # supplier partner, if there is confirm it with the specified quantity
        # if there isn't create new
        # The automatic parameter will allow us to know  if the  function is
        # triggered by cron job or manually
        # the automatic job will be triggered if stock levels are below

        product = self.product
        ultimate_purchase_to = self.ultimate_purchase_to
        po_model = self.env["purchase.order"]
        pol_model = self.env["purchase.order.line"]
        date_order = date.today().strftime(DSDF)
        qty = self._get_qty(product, self.supplier, self.stock_period_max)
        if qty > 0:
            order_vals = {
                "partner_id": self.supplier.name.id,
                "origin": "purchase proposal",
                "date_order": date_order, }
            purchase_order = po_model.create(order_vals)
            line_vals = {
                'name': 'Resupply of %s' % product.name,
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'product_qty': qty,
                'order_id': purchase_order.id,
                'date_planned': ultimate_purchase_to or datetime.today(),
                'price_unit': self.supplier.price
            }
            pol = pol_model.create(line_vals)
            pol._compute_amount()
            # ZERO IN  ULTIMATE PURCHASE WHEN  WRITE DONE
            product.write({"ultimate_purchase": False})
            return purchase_order
        return False

    product = fields.Many2one(
        "product.product",
        string="Product",
        readonly=1
    )
    location = fields.Many2one(
        "stock.location",
        string="Location",
        domain="[('usage', '=', 'internal')]"
    )
    supplier = fields.Many2one(
        "product.supplierinfo"
    )
    stock_avl = fields.Float("Currently available overall")
    ultimate_purchase = fields.Date("Ultimate purchase")
    pending_rfq_lines = fields.Many2many(
        "purchase.order.line", string="Pending requests")
    name = fields.Char(
        string="Name", size=256, readonly="1"
    )
    stock_period_min = fields.Integer(
        string="Delivery period",
        readonly="1",
        help="""Minimum stock for this supplier in days."""
    )
    stock_period_max = fields.Integer(
        string="Maximum stock",
        help="Default period for this supplier in days to resupply for."
    )
    ultimate_purchase_to = fields.Date(
        string="Date Planned"
    )
