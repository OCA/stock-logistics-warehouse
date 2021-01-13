# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestStockQuantManualAssign(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockQuantManualAssign, cls).setUpClass()
        cls.quant_model = cls.env['stock.quant']
        cls.move_model = cls.env['stock.move']
        cls.quant_assign_wizard = cls.env['assign.manual.quants']
        cls.product = cls.env['product.product'].create({
            'name': 'Product 4 test',
            'type': 'product',
        })
        cls.location_src = cls.env.ref(
            'stock.stock_location_locations_virtual')
        cls.location_dst = cls.env.ref('stock.stock_location_customers')
        cls.location1 = cls.env.ref('stock.location_inventory')
        cls.location2 = cls.env.ref('stock.location_procurement')
        cls.location3 = cls.env.ref('stock.location_production')
        cls.quant1 = cls.quant_model.sudo().create({
            'product_id': cls.product.id,
            'quantity': 100.0,
            'location_id': cls.location1.id,
        })
        cls.quant2 = cls.quant_model.sudo().create({
            'product_id': cls.product.id,
            'quantity': 100.0,
            'location_id': cls.location2.id,
        })
        cls.quant3 = cls.quant_model.sudo().create({
            'product_id': cls.product.id,
            'quantity': 100.0,
            'location_id': cls.location3.id,
        })
        cls.move = cls.move_model.create({
            'name': cls.product.name,
            'product_id': cls.product.id,
            'product_uom_qty': 400.0,
            'product_uom': cls.product.uom_id.id,
            'location_id': cls.location_src.id,
            'location_dest_id': cls.location_dst.id,
        })
        cls.move._action_confirm()

    def test_quant_assign_wizard(self):
        wizard = self.quant_assign_wizard.with_context(
            active_id=self.move.id).create({
            })
        self.assertEqual(len(wizard.quants_lines.ids), 3,
                         'Three quants created, three quants got by default')
        self.assertEqual(len(wizard.quants_lines.filtered('selected').ids), 0,
                         'None of the quants must have been selected')
        self.assertEqual(wizard.lines_qty, 0.0,
                         'None selected must give 0')
        self.assertEqual(sum(line.qty for line in wizard.quants_lines),
                         self.move.reserved_availability)
        self.assertEqual(wizard.move_qty, self.move.product_uom_qty)

    def test_quant_assign_wizard_constraint(self):
        wizard = self.quant_assign_wizard.with_context(
            active_id=self.move.id).create({
            })
        self.assertEqual(len(wizard.quants_lines.ids), 3,
                         'Three quants created, three quants got by default')
        self.assertEqual(len(wizard.quants_lines.filtered('selected').ids), 0,
                         'None of the quants must have been selected')
        self.assertEqual(wizard.lines_qty, 0.0,
                         'None selected must give 0')
        with self.assertRaises(ValidationError):
            wizard.write({'quants_lines': [(1, wizard.quants_lines[:1].id,
                                            {'selected': True, 'qty': 500})]})

    def test_quant_manual_assign(self):
        wizard = self.quant_assign_wizard.with_context(
            active_id=self.move.id).create({
            })
        self.assertEqual(len(wizard.quants_lines.ids), 3,
                         'Three quants created, three quants got by default')
        wizard.quants_lines[0].write({
            'selected': True,
        })
        wizard.quants_lines[0]._onchange_selected()
        wizard.quants_lines[1].write({
            'selected': True,
            'qty': 50.0,
        })
        self.assertEqual(wizard.lines_qty, 150.0)
        self.assertEqual(wizard.move_qty, 250.0)
        wizard.assign_quants()
        self.assertAlmostEqual(len(self.move.move_line_ids),
                               len(wizard.quants_lines.filtered('selected')))

    def test_quant_assign_wizard_after_availability_check(self):
        self.move._action_assign()
        wizard = self.quant_assign_wizard.with_context(
            active_id=self.move.id).create({
            })
        self.assertEqual(len(wizard.quants_lines.ids), 3,
                         'Three quants created, three quants got by default')
        self.assertEqual(len(wizard.quants_lines.filtered('selected').ids), 3,
                         'All the quants must have been selected')
        self.assertEqual(wizard.lines_qty, 300.0)
        self.assertEqual(wizard.move_qty, 100.0)
        self.assertEqual(len(wizard.quants_lines.filtered('selected')),
                         len(self.move.move_line_ids))
        self.assertEqual(sum(line.qty for line in wizard.quants_lines),
                         self.move.reserved_availability)
