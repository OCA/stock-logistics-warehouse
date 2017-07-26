# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common
from odoo import exceptions


class TestStockQuantManualAssign(common.TransactionCase):

    def setUp(self):
        super(TestStockQuantManualAssign, self).setUp()
        self.quant_model = self.env['stock.quant']
        self.move_model = self.env['stock.move']
        self.quant_assign_wizard = self.env['assign.manual.quants']
        self.product = self.env['product.product'].create({
            'name': 'Product 4 test',
            'type': 'product',
        })
        self.location_src = self.env.ref(
            'stock.stock_location_locations_virtual')
        self.location_dst = self.env.ref('stock.stock_location_customers')
        self.location1 = self.env.ref('stock.location_inventory')
        self.location2 = self.env.ref('stock.location_procurement')
        self.location3 = self.env.ref('stock.location_production')
        self.quant1 = self.quant_model.sudo().create({
            'product_id': self.product.id,
            'qty': 100.0,
            'location_id': self.location1.id,
        })
        self.quant2 = self.quant_model.sudo().create({
            'product_id': self.product.id,
            'qty': 100.0,
            'location_id': self.location2.id,
        })
        self.quant3 = self.quant_model.sudo().create({
            'product_id': self.product.id,
            'qty': 100.0,
            'location_id': self.location3.id,
        })
        self.move = self.move_model.create({
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom_qty': 400.0,
            'product_uom': self.product.uom_id.id,
            'location_id': self.location_src.id,
            'location_dest_id': self.location_dst.id,
        })
        self.move.action_confirm()

    def test_quant_assign_wizard(self):
        wizard = self.quant_assign_wizard.with_context(
            active_id=self.move.id).create({
                'name': 'New wizard',
            })
        self.assertEqual(len(wizard.quants_lines.ids), 3,
                         'Three quants created, three quants got by default')
        self.assertEqual(len(wizard.quants_lines.filtered('selected').ids), 0,
                         'None of the quants must have been selected')
        self.assertEqual(wizard.lines_qty, 0.0,
                         'None selected must give 0')
        for line in wizard.quants_lines:
            if line.quant in self.move.reserved_quant_ids:
                self.assertTrue(line.selected)
            else:
                self.assertFalse(line.selected)
        self.assertEqual(wizard.move_qty, self.move.product_uom_qty)

    def test_quant_assign_wizard_constraint(self):
        wizard = self.quant_assign_wizard.with_context(
            active_id=self.move.id).create({
                'name': 'New wizard',
            })
        self.assertEqual(len(wizard.quants_lines.ids), 3,
                         'Three quants created, three quants got by default')
        self.assertEqual(len(wizard.quants_lines.filtered('selected').ids), 0,
                         'None of the quants must have been selected')
        self.assertEqual(wizard.lines_qty, 0.0,
                         'None selected must give 0')
        with self.assertRaises(exceptions.ValidationError):
            wizard.write({'quants_lines': [(1, wizard.quants_lines[:1].id,
                                            {'selected': True, 'qty': 500})]})

    def test_quant_manual_assign(self):
        wizard = self.quant_assign_wizard.with_context(
            active_id=self.move.id).create({
                'name': 'New wizard',
            })
        self.assertEqual(len(wizard.quants_lines.ids), 3,
                         'Three quants created, three quants got by default')
        wizard.quants_lines[0].write({
            'selected': True,
        })
        wizard.quants_lines[0].onchange_selected()
        wizard.quants_lines[1].write({
            'selected': True,
            'qty': 50.0,
        })
        self.assertEqual(wizard.lines_qty, 150.0)
        self.assertEqual(wizard.move_qty, 250.0)
        wizard.assign_quants()
        self.assertEqual(len(wizard.quants_lines.filtered('selected')),
                         len(self.move.reserved_quant_ids))
        selected_quants = wizard.quants_lines.filtered(
            'selected').mapped('quant')
        self.assertEqual(
            sum(self.move.reserved_quant_ids.mapped('qty')),
            wizard.lines_qty)
        for quant in self.move.reserved_quant_ids:
            self.assertTrue(quant in selected_quants)
        wizard.assign_quants()
        self.assertEqual(len(wizard.quants_lines.filtered('selected')),
                         len(self.move.reserved_quant_ids))

    def test_quant_assign_wizard_after_availability_check(self):
        self.move.action_assign()
        wizard = self.quant_assign_wizard.with_context(
            active_id=self.move.id).create({
                'name': 'New wizard',
            })
        self.assertEqual(len(wizard.quants_lines.ids), 3,
                         'Three quants created, three quants got by default')
        self.assertEqual(len(wizard.quants_lines.filtered('selected').ids), 3,
                         'All the quants must have been selected')
        self.assertEqual(wizard.lines_qty, 300.0)
        self.assertEqual(wizard.move_qty, 100.0)
        for line in wizard.quants_lines:
            if line.quant in self.move.reserved_quant_ids:
                self.assertTrue(line.selected)
            else:
                self.assertFalse(line.selected)
