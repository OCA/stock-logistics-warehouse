# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase
from odoo.exceptions import ValidationError


class TestSerialBatchGenerator(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        location_stock = cls.env.ref('stock.stock_location_stock')
        location_customers = cls.env.ref('stock.stock_location_customers')
        partner = cls.env.ref('base.partner_demo')
        picking_type = cls.env.ref('stock.picking_type_in')
        picking_type.use_create_lots = True
        product = cls.env.ref('product.product_product_5')
        product.tracking = 'serial'
        product.type = 'consu'

        picking = cls.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': location_stock.id,
            'location_dest_id': location_customers.id,
            'partner_id': partner.id,
        })
        cls.move = cls.env['stock.move'].create({
            'name': 'Test move',
            'product_id': product.id,
            'product_uom': cls.env.ref('uom.product_uom_unit').id,
            'product_uom_qty': 5,
            'location_id': location_stock.id,
            'location_dest_id': location_customers.id,
            'picking_id': picking.id,
            'picking_type_id': picking_type.id,
        })
        picking.action_assign()
        cls.wizard = cls.env['stock.move.line.serial.generator'].create(
            {'stock_move_id': cls.move.id}
        )

    def test_01_genrate_batch_serials(self):
        # serials numbers successfully created
        self.wizard.qty_to_process = 5
        self.wizard.first_number = 23
        self.wizard.generate_serials()
        serials = self.wizard.stock_move_id.mapped('move_line_ids.lot_name')
        exp_serials = ['23', '24', '25', '26', '27']
        self.assertEqual(serials, exp_serials)

    def test_02_genrate_batch_serials(self):
        # check error handlings
        with self.assertRaises(ValidationError):
            # can't set bigger amount than total qty in the move
            self.wizard.qty_to_process = 15
        self.wizard.first_number = 56
        self.wizard.qty_to_process = 5
        self.wizard.first_number = 56
        self.wizard.generate_serials()
        with self.assertRaises(ValidationError):
            # serial numbers are aleready in a use
            self.wizard.generate_serials()

    def test_03_genrate_and_merge_batch_serials(self):
        # create serial numbers only where they needed
        self.move.move_line_ids[3].lot_name = '12345'
        self.wizard.qty_to_process = 4
        self.wizard.first_number = 23
        self.wizard.generate_serials()
        serials = self.wizard.stock_move_id.mapped('move_line_ids.lot_name')
        exp_serials = ['23', '24', '25', '12345', '26']
        self.assertEqual(serials, exp_serials)
