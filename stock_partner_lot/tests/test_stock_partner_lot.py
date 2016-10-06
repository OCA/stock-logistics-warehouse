# (c) 2016 credativ ltd. - Ondřej Kuzník
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
"""Unit Test of Stock Partner Lot"""

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.product.tests import common

class TestStockPartnerLot(common.TestProductCommon):
    """Testing Session"""
    def setUp(self):
        """Defining initial"""
        super(TestStockPartnerLot, self).setUp()
        self.partner_id = self.env.ref('base.res_partner_1')
        self.product_1 = self.env.ref('product.product_product_5')
        self.product_2 = self.env.ref('product.product_product_6')

        res_users_purchase_user = self.env.ref('purchase.group_purchase_user')
        user = self.env['res.users'].with_context({'no_reset_password': True,
                                                   'mail_create_nosubscribe': True})
        self.purchase_user = user.create({
            'name': 'Agung Rachmatullah',
            'login': 'agung_r',
            'email': 'agung@email.com',
            'groups_id': [(6, 0, [res_users_purchase_user.id])]
        })

        self.purchase_order = self.env['purchase.order']

    def test_receipt(self):
        """Create draft PO and confirm it, then in its picking,
            edit the owner of product"""
        # Activate Consignment settings
        self.env['res.config.settings'].create({
            'group_stock_tracking_owner': True,
        })

        # Create draft PO
        po_1 = self.purchase_order.create({
            'partner_id': self.partner_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_1.name,
                    'product_id': self.product_1.id,
                    'product_uom': self.product_1.uom_po_id.id,
                    'price_unit': 750.0,
                    'product_qty': 10.0,
                    'date_planned': datetime.today().strftime\
                        (DEFAULT_SERVER_DATETIME_FORMAT),
                }),
                (0, 0, {
                    'name': self.product_2.name,
                    'product_id': self.product_2.id,
                    'product_uom': self.product_2.uom_po_id.id,
                    'price_unit': 250.0,
                    'product_qty': 8.0,
                    'date_planned': datetime.today().strftime\
                        (DEFAULT_SERVER_DATETIME_FORMAT),
                })
            ],
        })

        # Confirm the PO
        po_1.button_confirm()

        # Validate first shipment
        picking = po_1.picking_ids[0]
        picking.force_assign()
        for move_line in picking.move_line_ids:
            move_line.write({
                'qty_done': move_line.product_uom_qty,
                'owner_id': self.partner_id.id,
                'lot_name': move_line.product_id.name,
            })
        picking.action_done()

        # Assert Session
        total_product = len(self.env['stock.quant'].\
                            search([('owner_id', '=', self.partner_id.id)]))
        self.assertEqual(self.partner_id.quant_count, total_product)
