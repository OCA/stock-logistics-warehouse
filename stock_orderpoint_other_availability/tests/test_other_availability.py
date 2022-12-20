#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import tests
from odoo.tests import Form


class TestOtherAvailabilityOrderPoint (tests.SavepointCase):

    @classmethod
    def _assign_new_quantity(cls, product, quantity):
        """Update the quantity of `product` to `quantity`."""
        # Build the wizard for changing the quantity
        change_qty_action = product.action_update_quantity_on_hand()
        change_qty_wiz_model = change_qty_action.get('res_model')
        change_qty_wiz_id = change_qty_action.get('res_id')
        change_qty_wiz_context = change_qty_action.get('context') or {}
        change_qty_wiz = cls.env[change_qty_wiz_model] \
            .browse(change_qty_wiz_id) \
            .with_context(**change_qty_wiz_context)

        # Change the quantity with the wizard
        change_qty_wiz_form = Form(change_qty_wiz)
        change_qty_wiz_form.new_quantity = quantity
        change_qty_wiz = change_qty_wiz_form.save()
        change_qty_wiz_result = change_qty_wiz.change_product_qty()
        return change_qty_wiz_result

    @classmethod
    def _assign_route(cls, product):
        """Create a supply rout for `product`.

        This is needed to run the scheduler because we don't have any module
        for replenishing the products when an orderpoint is triggered.
        """
        warehouse_model = cls.env['stock.warehouse']
        warehouse_2 = warehouse_model.create({
            'name': 'Small Warehouse',
            'code': 'SWH'
        })
        warehouse_1 = warehouse_model.search(
            [
                ('company_id', '=', cls.env.user.id),
            ],
            limit=1,
        )
        warehouse_1.write({
            'resupply_wh_ids': [(6, 0, warehouse_2.ids)],
        })

        resupply_route = cls.env['stock.location.route'].search(
            [
                ('supplier_wh_id', '=', warehouse_2.id),
                ('supplied_wh_id', '=', warehouse_1.id),
            ],
        )
        product.update({
            'route_ids': [
                (4, resupply_route.id),
                (4, cls.env.ref('stock.route_warehouse0_mto').id),
            ],
        })
        return resupply_route

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_model = cls.env['product.product']
        main_product_form = Form(product_model)
        main_product_form.name = "Test main product"
        main_product_form.type = 'product'
        cls.main_product = main_product_form.save()
        cls.resupply_route = cls._assign_route(cls.main_product)
        cls._assign_new_quantity(cls.main_product, 1)

        other_product_form = Form(product_model)
        other_product_form.name = "Test other product"
        other_product_form.type = 'product'
        cls.other_product = other_product_form.save()
        cls._assign_new_quantity(cls.other_product, 5)

        orderpoint_form = Form(cls.env['stock.warehouse.orderpoint'])
        orderpoint_form.product_id = cls.main_product
        orderpoint_form.product_min_qty = 0
        orderpoint_form.product_max_qty = 50
        orderpoint_form.qty_multiple = 1
        orderpoint_form.is_other_availability = True
        orderpoint_form.other_availability_product_id = cls.other_product
        orderpoint_form.other_availability_qty = 10
        cls.orderpoint = orderpoint_form.save()

    def test_other_availability_orderpoint(self):
        """When there is not enough of `other_availability_product_id`,
        the orderpoint is triggered."""
        # Arrange
        orderpoint = self.orderpoint
        product = orderpoint.product_id
        availability_product = orderpoint.other_availability_product_id
        self._assign_new_quantity(product, 1)
        self._assign_new_quantity(availability_product, 5)
        # pre-conditions: the orderpoint is for other availability,
        # and it will be triggered because
        # the `other_availability_product_id` has less availability
        # than requested by `other_availability_qty`
        self.assertTrue(orderpoint.is_other_availability)
        self.assertLess(
            availability_product.virtual_available,
            orderpoint.other_availability_qty,
        )
        self.assertEqual(orderpoint.product_max_qty, 50)
        self.assertEqual(product.virtual_available, 1)
        self.assertGreater(product.virtual_available, orderpoint.product_min_qty)

        # Act
        self.env['procurement.group'].run_scheduler()

        # Assert
        rule = self.resupply_route.rule_ids[-1]
        pull_move = self.env['stock.move'].search(
            [
                ('rule_id', '=', rule.id),
            ],
        )
        self.assertEqual(len(pull_move), 1)
        self.assertEqual(pull_move.product_uom_qty, 50 - 1)
