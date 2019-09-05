# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase
from odoo.exceptions import ValidationError


class TestStockMoveLocationDestConstraintEmpty(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # workplace has a quant of 16 on Shelf 2
        cls.product_workplace = cls.env.ref('product.product_product_24')
        cls.product_flipover = cls.env.ref('product.product_product_20')
        cls.location_shelf_2 = cls.env.ref('stock.stock_location_14')
        cls.location_shelf_2.write({'bypass_constraints': False})
        cls.location_shelf_3 = cls.env.ref(
            'stock_move_location_dest_constraint_empty.location_shelf_3'
        )
        cls.location_vendors = cls.env.ref('stock.stock_location_suppliers')

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

    def test_existing_quant_restricted(self):
        with self.assertRaises(ValidationError):
            self._create_and_assign_move(
                self.product_flipover, self.location_vendors,
                self.location_shelf_2
            )

    def test_existing_planned_move_restricted(self):
        move = self._create_and_assign_move(
            self.product_workplace, self.location_shelf_2,
            self.location_shelf_3
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_shelf_3
        )
        with self.assertRaises(ValidationError):
            self._create_and_assign_move(
                self.product_flipover, self.location_vendors,
                self.location_shelf_2
            )
