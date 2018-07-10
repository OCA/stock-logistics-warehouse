# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime
from odoo.tests import common


class SameLocationPutawayCase(common.SavepointCase):

    post_install = True
    at_install = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Common data
        cls.location_stock = cls.env.ref('stock.stock_location_stock')
        cls.location_customers = cls.env.ref('stock.stock_location_customers')
        cls.location_suppliers = cls.env.ref('stock.stock_location_suppliers')

        tested_putaway_strategy = cls.env['product.putaway'].create({
            'name': 'Tested putaway strategy',
            'method': 'previous/empty',
        })
        cls.location_stock.putaway_strategy_id = tested_putaway_strategy
        cls.any_customer = cls.env['res.partner'].search([
            ('customer', '=', True),
        ])

        # Sublocations, a.k.a. "bins"
        cls.bins = cls.env['stock.location']

        # Prevent other sub-stock locations from being considered the closest
        cls.env['stock.location'].search([
            ('id', 'child_of', cls.location_stock.id),
            ('id', '!=', cls.location_stock.id),
        ]).write({
            'posx': 100,
            'posy': 100,
            'posz': 100,
        })

        for bin_number, coords in enumerate([
                (1, 1, 1),
                (2, 1, 1),
                (1, 2, 1),
                (2, 2, 1),
                (1, 3, 1),
                (2, 3, 1),
                (1, 1, 2),
        ], start=1):
            x, y, z = coords
            new_bin = cls.location_stock.create({
                'name': 'Bin #{} @ {}:{}:{}'.format(bin_number, x, y, z),
                'location_id': cls.location_stock.id,
                'usage': 'internal',
                'posx': x,
                'posy': y,
                'posz': z,
            })
            cls.bins |= new_bin

        # recompute `parent_left` and `parent_right`
        cls.env['stock.location']._parent_store_compute()

        # Products (differ in tracking)
        cls.product_a_untracked = cls.env['product.product'].create({
            'name': 'Sample product (untracked)',
            'tracking': 'none',
            'type': 'product',
        })
        cls.product_b_lots = cls.env['product.product'].create({
            'name': 'Sample product (tracked by lots)',
            'tracking': 'lot',
            'type': 'product',
        })
        cls.product_c_serial = cls.env['product.product'].create({
            'name': 'Sample product (tracked by SN-s)',
            'tracking': 'serial',
            'type': 'product',
        })

    @staticmethod
    def _get_order_line_common_vals(product, qty2order):
        """Assemble vals for `purchase.order.line` creation."""
        return {
            'product_id': product.id,
            'product_qty': float(qty2order),
            # trash required by model's `create()`
            'name': '{} {} of {}'.format(
                qty2order, product.uom_id.name, product.name),
            'date_planned': datetime.today(),
            'product_uom': product.uom_id.id,
            'price_unit': 1337.,
        }

    @classmethod
    def _create_picking(cls, location_from, location_to, move_details):
        """create and validate a picking w/ given move values.

        :param location_from: singleton of `stock.location`
        :param location_to: singleton of `stock.location`
        :param move_details: [
            (<product1>, <qty of product1>),
            ...
        ]
        :param process_immediately: whether to confirm picking after creation
        """
        picking = cls.env['stock.picking'].create({
            'location_id': location_from.id,
            'location_dest_id': location_to.id,
            'picking_type_id': cls.env.ref('stock.picking_type_in').id,
            'move_lines': [
                (0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom': product.uom_id.id,
                    'product_uom_qty': qty,
                })
                for product, qty in move_details
            ],
        })
        return picking

    @classmethod
    def _process_picking(cls, picking, move_details=None, apply_putaway=True):
        """Process created picking.

        :param move_details: [
            (<product1>, <product1 lot/SN>),
            ...
        ]
        """
        picking.ensure_one()
        picking.action_assign()
        if not move_details:
            move_details = []
        for product, lot_name in move_details:
            current_product_move_line = picking.move_line_ids.filtered(
                lambda line: line.product_id == product)
            if lot_name:
                lot = cls.env['stock.production.lot'].search([
                    ('name', '=', lot_name),
                ])
                if not lot:
                    lot = cls.env['stock.production.lot'].create({
                        'name': lot_name,
                        'product_id': product.id,
                    })
                current_product_move_line.lot_id = lot
        if not apply_putaway:
            for move_line in picking.move_line_ids:
                move_line.location_dest_id = picking.location_dest_id
        cls.env['stock.immediate.transfer'].create({
            'pick_ids': [(6, 0, picking.ids)],
        }).process()

    def _assert_amount_in_bin(self, product, bin_, xpected_qty):
        self.assertAlmostEqual(product.with_context(
            location=bin_.id,
            compute_child=False,
        ).qty_available, float(xpected_qty))

    def _assert_empty(self, location):
        self.assertAlmostEqual(sum(location.mapped('quant_ids.quantity')), 0.)

    # TODO add a counterpart which tests the opposite case
    # i.e., putaway method is `fixed`
    def test_putaway_scenario_last_or_empty(self):
        # STEP 1: confirm PO00001
        # untracked (x10) => bins[0] // as an unknown product (first empty)
        po1 = self._create_picking(
            self.location_suppliers, self.location_stock, [
                (self.product_a_untracked, 10),
            ])
        self._assert_empty(self.bins[0])
        self._process_picking(po1, [
            (self.product_a_untracked, False),
        ])
        self._assert_amount_in_bin(self.product_a_untracked, self.bins[0], 10)

        # STEP 2: confirm PO00002
        # untracked (x10) => bins[0] // as a most recent destination location
        # by lots   (x20) => bins[1] // as an unknown product (first empty)
        po2 = self._create_picking(
            self.location_suppliers, self.location_stock, [
                (self.product_a_untracked, 10),
                (self.product_b_lots, 20),
            ])
        self._assert_empty(self.bins[1])
        self._process_picking(po2, [
            (self.product_a_untracked, False),
            (self.product_b_lots, '001'),
        ])
        self._assert_amount_in_bin(self.product_a_untracked, self.bins[0], 20)
        self._assert_amount_in_bin(self.product_b_lots, self.bins[1], 20)

        # Step 2.5: manually move 10x of lot 001 // bins[1] => bins[3]
        # NOTE: bins[1] won't become empty after confirmation
        # cause that one holds 20 pcs of it ATM
        intermediate_picking_1 = self._create_picking(
            self.bins[1], self.bins[3], [
                (self.product_b_lots, 10),
            ])
        self._process_picking(intermediate_picking_1, [
            (self.product_b_lots, '001'),
        ], apply_putaway=False)
        self._assert_amount_in_bin(self.product_b_lots, self.bins[3], 10)

        # STEP 3: confirm PO00003
        # by lots   (x15) => bins[3] // as a most recent destination location
        # by SN-s   ( x1) => bins[2] // as an unknown product (first empty)
        self._assert_empty(self.bins[2])
        po3 = self._create_picking(
            self.location_suppliers, self.location_stock, [
                (self.product_b_lots, 15),
                (self.product_c_serial, 1),
            ])
        self._process_picking(po3, [
            (self.product_b_lots, '001'),
            (self.product_c_serial, '002'),
        ])
        # ensure that putaway strategy respects move that happened on step 2.5
        self._assert_amount_in_bin(self.product_b_lots, self.bins[3], 25)
        self._assert_amount_in_bin(self.product_c_serial, self.bins[2], 1)

        # STEP 4: confirm PO00004
        # by lots   (x10) => bins[3] // as a most recent destination location
        # by SN-s   ( x1) => bins[2] // as a most recent destination location
        po4 = self._create_picking(
            self.location_suppliers, self.location_stock, [
                (self.product_b_lots, 10),
                (self.product_c_serial, 1),
            ])
        self._process_picking(po4, [
            (self.product_b_lots, '003'),
            (self.product_c_serial, '005'),
        ])
        self._assert_amount_in_bin(self.product_b_lots, self.bins[3], 35)
        # ensure that bins[2] holds two products tracked by SN-s
        self._assert_amount_in_bin(self.product_c_serial, self.bins[2], 2)

        # Step 4.5: Create a delivery for 45 product B
        # NOTE: this dries out the whole product B stock
        intermediate_picking_2 = self._create_picking(
            self.location_stock, self.location_customers, [
                (self.product_b_lots, 45.),
            ])
        self._process_picking(intermediate_picking_2)
        self._assert_empty(self.bins[1])
        self._assert_empty(self.bins[3])

        # STEP 5: confirm PO00005
        # by lots   (x20) => bins[3] // as a most recent destination location
        po5 = self._create_picking(
            self.location_suppliers, self.location_stock, [
                (self.product_b_lots, 20),
            ])
        self._process_picking(po5, [
            (self.product_b_lots, '004'),
        ])
        self._assert_amount_in_bin(self.product_b_lots, self.bins[3], 20)
