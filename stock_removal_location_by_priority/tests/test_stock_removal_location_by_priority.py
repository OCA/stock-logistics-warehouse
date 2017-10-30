# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestStockRemovalLocationByPriority(TransactionCase):

    def setUp(self):
        super(TestStockRemovalLocationByPriority, self).setUp()
        self.res_users_model = self.env['res.users']
        self.stock_location_model = self.env['stock.location']
        self.stock_warehouse_model = self.env['stock.warehouse']
        self.stock_picking_model = self.env['stock.picking']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.product_template_model = self.env['product.template']
        self.quant_model = self.env['stock.quant']

        self.picking_internal = self.env.ref('stock.picking_type_internal')
        self.picking_out = self.env.ref('stock.picking_type_out')
        self.location_supplier = self.env.ref('stock.stock_location_suppliers')

        self.company = self.env.ref('base.main_company')
        self.grp_rem_priority = self.env.ref(
            'stock_removal_location_by_priority.group_removal_priority')

        self.g_stock_user = self.env.ref('stock.group_stock_user')

        self.user = self._create_user(
            'user_1', [self.g_stock_user, self.grp_rem_priority],
            self.company).id

        self.wh1 = self.stock_warehouse_model.create({
            'name': 'WH1',
            'code': 'WH1',
        })

        # Create a locations:
        self.stock = self.stock_location_model.create({
            'name': 'Stock Base',
            'usage': 'internal',
        })
        self.shelf_A = self.stock_location_model.create({
            'name': 'Shelf_A',
            'usage': 'internal',
            'location_id': self.stock.id,
        })
        self.shelf_B = self.stock_location_model.create({
            'name': 'Shelf_B',
            'usage': 'internal',
            'location_id': self.stock.id,
            'removal_priority': 5,
        })

        # Create a product:
        self.product_templ_1 = self.product_template_model.create({
            'name': 'Test Product Template 1',
            'type': 'product',
            'default_code': 'PROD_1',
        })

    def _create_user(self, login, groups, company):
        group_ids = [group.id for group in groups]
        user = self.res_users_model.create({
            'name': login,
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'groups_id': [(6, 0, group_ids)]
        })
        return user

    def _create_picking(self, picking_type, location, location_dest, qty):

        picking = self.stock_picking_model.sudo(self.user).create({
            'picking_type_id': picking_type.id,
            'location_id': location.id,
            'location_dest_id': location_dest.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': self.product1.id,
                    'product_uom': self.product1.uom_id.id,
                    'product_uom_qty': qty,
                    'location_id': location.id,
                    'location_dest_id': location_dest.id,
                    'price_unit': 2
                })]
        })
        return picking

    def test_stock_removal_location_by_priority_fifo(self):
        """Tests removal priority."""
        wiz1 = self.stock_change_model.with_context(
            active_id=self.product_templ_1.id,
            active_model='product.template'
        ).create({'new_quantity': 20,
                  'location_id': self.stock.id,
                  'product_tmpl_id': self.product_templ_1.id,
                  })
        wiz1.change_product_qty()
        self.product1 = wiz1.product_id

        picking_1 = self._create_picking(
            self.picking_internal, self.stock, self.shelf_A, 5)
        picking_1.action_confirm()
        picking_1.action_assign()

        picking_2 = self._create_picking(
            self.picking_internal, self.stock, self.shelf_B, 10)
        picking_2.action_confirm()
        picking_2.action_assign()

        self.assertEqual(picking_1.pack_operation_ids.
                         linked_move_operation_ids.reserved_quant_id.in_date,
                         picking_2.pack_operation_ids.
                         linked_move_operation_ids.reserved_quant_id.in_date,
                         'Testing data not generated properly.')

        wiz_act = picking_1.do_new_transfer()
        wiz2 = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz2.process()

        wiz_act = picking_2.do_new_transfer()
        wiz3 = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz3.process()

        picking_3 = self._create_picking(
            self.picking_out, self.stock, self.location_supplier, 5)
        picking_3.action_confirm()
        picking_3.action_assign()
        wiz_act = picking_3.do_new_transfer()
        wiz4 = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz4.process()

        records = self.quant_model.search(
            [('product_id', '=', self.product1.id)])
        for record in records:
            self.assertEqual(record.qty, 5,
                             'Removal_priority did\'nt work properly.')

    def test_stock_removal_location_by_priority_lifo(self):
        """Tests removal priority."""
        removal_method_id = self.env['product.removal'].search(
            [('name', '=', 'lifo')]).id
        self.stock.removal_strategy_id = removal_method_id
        self.shelf_A.removal_strategy_id = removal_method_id
        self.shelf_B.removal_strategy_id = removal_method_id
        self.location_supplier.removal_strategy_id = removal_method_id
        wiz1 = self.stock_change_model.with_context(
            active_id=self.product_templ_1.id,
            active_model='product.template'
        ).create({'new_quantity': 20,
                  'location_id': self.stock.id,
                  'product_tmpl_id': self.product_templ_1.id,
                  })
        wiz1.change_product_qty()
        self.product1 = wiz1.product_id

        picking_1 = self._create_picking(
            self.picking_internal, self.stock, self.shelf_A, 5)
        picking_1.action_confirm()
        picking_1.action_assign()

        picking_2 = self._create_picking(
            self.picking_internal, self.stock, self.shelf_B, 10)
        picking_2.action_confirm()
        picking_2.action_assign()

        self.assertEqual(picking_1.pack_operation_ids.
                         linked_move_operation_ids.reserved_quant_id.in_date,
                         picking_2.pack_operation_ids.
                         linked_move_operation_ids.reserved_quant_id.in_date,
                         'Testing data not generated properly.')

        wiz_act = picking_1.do_new_transfer()
        wiz2 = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz2.process()

        wiz_act = picking_2.do_new_transfer()
        wiz3 = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz3.process()

        picking_3 = self._create_picking(
            self.picking_out, self.stock, self.location_supplier, 5)
        picking_3.action_confirm()
        picking_3.action_assign()
        wiz_act = picking_3.do_new_transfer()
        wiz4 = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz4.process()

        records = self.quant_model.search(
            [('product_id', '=', self.product1.id)])
        for record in records:
            self.assertEqual(record.qty, 5,
                             'Removal_priority did\'nt work properly.')
