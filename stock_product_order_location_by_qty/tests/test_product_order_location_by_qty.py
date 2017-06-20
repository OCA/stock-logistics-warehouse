# coding: utf-8
# © 2017 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.tests import common


class TestProductOrderLocationByQty(common.TransactionCase):
    def test_product_order_location_by_qty(self):
        product_ipad = self.browse_ref(
            'product.product_product_4')
        location_shelf1 = self.browse_ref(
            'stock.stock_location_components')
        location_shelf2 = self.browse_ref(
            'stock.stock_location_14')

        wiz_obj = self.env['stock.change.product.qty']

        test_context = {
            'active_model': 'product.product',
            'active_id': product_ipad.id,
        }
        wiz_instance1 = wiz_obj.with_context(test_context).create({
            'location_id': location_shelf1.id,
            'new_quantity': 12.0
        })
        wiz_instance1.change_product_qty()
        wiz_instance2 = wiz_obj.with_context(test_context).create({
            'location_id': location_shelf2.id,
            'new_quantity': 25.0
        })
        wiz_instance2.change_product_qty()
        wiz_instance = wiz_obj.with_context(test_context).create({})
        import pdb;pdb.set_trace()