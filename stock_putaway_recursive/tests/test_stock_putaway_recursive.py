# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class TestStockPutawayRecursive(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_flipover = cls.env.ref('product.product_product_20')
        cls.order_location = cls.env.ref('stock.location_order')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.shelf1_location = cls.env.ref('stock.stock_location_components')
        cls.shelf2_location = cls.env.ref('stock.stock_location_14')
        cls.refri_location = cls.env.ref('stock.location_refrigerator_small')

        # Define putaway from Stock to Stock/Shelf 2
        stock_putaway = cls.env['product.putaway'].create({
            'name': 'stock putaway',
        })
        cls.stock_location.write({
            'putaway_strategy_id': stock_putaway.id
        })
        stock_putaway.write({
            'product_location_ids': [(0, 0, {
                'product_id': cls.product_flipover.id,
                'fixed_location_id': cls.shelf2_location.id,
            })]
        })
        # Define putaway from Stock/Shelf 2 to Stock/Shelf 2/Small refrigerator
        shelf2_putaway = cls.env['product.putaway'].create({
            'name': 'shelf2 putaway',
        })
        cls.shelf2_location.write({
            'putaway_strategy_id': shelf2_putaway.id
        })
        shelf2_putaway.write({
            'product_location_ids': [(0, 0, {
                'product_id': cls.product_flipover.id,
                'fixed_location_id': cls.refri_location.id,
            })]
        })

    @classmethod
    def _update_qty_in_location(cls, location, product, quantity):
        cls.env['stock.quant']._update_available_quantity(
            product, location, quantity
        )

    def _create_and_assign_move(self, product, location, location_dest):
        move = self.env['stock.move'].create({
            'name': 'Test move',
            'product_id': product.id,
            'product_uom_qty': 1.0,
            'product_uom': product.uom_id.id,
            'location_id': location.id,
            'location_dest_id': location_dest.id,
        })
        move._action_confirm()
        move._action_assign()
        return move

    def test_putaway_recursive(self):
        self._update_qty_in_location(
            self.order_location, self.product_flipover, 10.0
        )
        move = self._create_and_assign_move(
            self.product_flipover, self.order_location, self.stock_location
        )
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.refri_location
        )
