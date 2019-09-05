# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class TestStockMoveLocationDestConstraintTag(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_sulfuric_acid = cls.env.ref(
            'stock_move_location_dest_constraint_tag.'
            'product_product_sulfuric_acid'
        )
        cls.product_ammonium = cls.env.ref(
            'stock_move_location_dest_constraint_tag.'
            'product_product_ammonium_nitrate'
        )
        cls.product_ice_cream = cls.env.ref(
            'stock_move_location_dest_constraint_tag.product_product_ice_cream'
        )
        cls.product_tnt = cls.env.ref(
            'stock_move_location_dest_constraint_tag.product_product_tnt'
        )

        cls.location_freezer = cls.env.ref(
            'stock_move_location_dest_constraint_tag.'
            'location_freezer_dangerous'
        )
        cls.location_refri = cls.env.ref(
            'stock.location_refrigerator_small'
        )
        cls.location_acids = cls.env.ref(
            'stock_move_location_dest_constraint_tag.location_bin_acids'
        )
        cls.location_dangerous = cls.env.ref(
            'stock_move_location_dest_constraint_tag.location_bin_dangerous'
        )
        cls.location_stock = cls.env.ref('stock.stock_location_stock')

        products_to_init = (
            cls.product_ice_cream | cls.product_ammonium |
            cls.product_sulfuric_acid | cls.product_tnt
        )
        for product in products_to_init:
            cls._update_qty_in_location(cls.location_stock, product, 100)

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

    def test_manual_move_category_restricted(self):
        # Acid category is liquid + dangerous
        # Putaway on acid category is on location acid
        # Location acid is liquid + dangerous
        move = self._create_and_assign_move(
            self.product_sulfuric_acid, self.location_stock,
            self.location_acids
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_acids
        )
        # Location freezer is cold + dangerous
        move = self._create_and_assign_move(
            self.product_sulfuric_acid, self.location_stock,
            self.location_freezer
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_acids
        )
        # Location dangerous is dangerous only
        move = self._create_and_assign_move(
            self.product_sulfuric_acid, self.location_stock,
            self.location_dangerous
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_acids
        )
        # Location refri is cold only
        move = self._create_and_assign_move(
            self.product_sulfuric_acid, self.location_stock,
            self.location_refri
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_acids
        )
        # Dangerous category is dangerous only
        # Putaway on dangerous category is on location dangerous
        # Location dangerous is dangerous only
        move = self._create_and_assign_move(
            self.product_tnt, self.location_stock, self.location_dangerous
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_dangerous
        )
        # Location freezer is cold + dangerous
        move = self._create_and_assign_move(
            self.product_tnt, self.location_stock,
            self.location_freezer
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_dangerous
        )
        # Location acid is liquid + dangerous
        move = self._create_and_assign_move(
            self.product_tnt, self.location_stock, self.location_acids
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_dangerous
        )
        # Location refri is cold only
        move = self._create_and_assign_move(
            self.product_tnt, self.location_stock,
            self.location_refri
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_dangerous
        )

    def test_manual_move_product_restricted(self):
        # Ammonium nitrate is cold + dangerous
        # Putaway on ammonium nitrate is on location freezer
        # Location freezer is cold + dangerous
        move = self._create_and_assign_move(
            self.product_ammonium, self.location_stock, self.location_freezer
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_freezer
        )
        # Location acid is liquid + dangerous
        move = self._create_and_assign_move(
            self.product_ammonium, self.location_stock, self.location_acids
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_freezer
        )
        # Location dangerous is dangerous only
        move = self._create_and_assign_move(
            self.product_ammonium, self.location_stock, self.location_dangerous
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_freezer
        )
        # Location refri is cold only
        move = self._create_and_assign_move(
            self.product_ammonium, self.location_stock, self.location_refri
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_freezer
        )
        # Ice cream product is cold only
        # Putaway on ice cream is on location refri
        # Location refri is cold only
        move = self._create_and_assign_move(
            self.product_ice_cream, self.location_stock, self.location_refri
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_refri
        )
        # Location freezer is cold + dangerous
        move = self._create_and_assign_move(
            self.product_ice_cream, self.location_stock, self.location_freezer
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_refri
        )
        # Location acid is liquid + dangerous
        self._create_and_assign_move(
            self.product_ice_cream, self.location_stock,
            self.location_dangerous
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_refri
        )
        # Location dangerous is dangerous only
        self._create_and_assign_move(
            self.product_ice_cream, self.location_stock,
            self.location_dangerous
        )
        self.assertEqual(move.state, 'assigned')
        self.assertEqual(
            move.move_line_ids.location_dest_id, self.location_refri
        )
