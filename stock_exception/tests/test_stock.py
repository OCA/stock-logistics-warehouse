from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
    def setUp(self):
        super(TestStockPicking, self).setUp()
        stock_location = self.env.ref("stock.stock_location_stock")
        customer_location = self.env.ref("stock.stock_location_customers")
        product = self.env.ref("product.product_product_4")
        picking_type = self.env.ref("stock.picking_type_out")
        # Create a picking in 'assigned' state with exceptions
        self.picking_with_exceptions = self.env["stock.picking"].create(
            {
                "name": "Test Picking With Exceptions 2",
                "state": "assigned",
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "picking_type_id": picking_type.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Move With Exceptions",
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "reserved_availability": 1,
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
                    )
                ],
                "ignore_exception": False,
            }
        )

        self.exception = self.env["exception.rule"].create(
            {
                "name": "Demand Quantity not positive",
                "sequence": 50,
                "model": "stock.move",
                "code": "if self.product_uom_qty == 0: failed=True",
                "active": True,
            }
        )

    def test_detect_exceptions(self):
        # Test that exceptions are detected for the picking with exceptions
        exceptions = self.picking_with_exceptions.detect_exceptions()
        self.assertFalse(exceptions, "Exceptions shouldn't be detected")
        move = self.picking_with_exceptions.move_ids[0]
        move.write({"product_uom_qty": 0})
        exceptions = self.picking_with_exceptions.detect_exceptions()
        self.assertTrue(exceptions, "Exceptions should be detected")

    def test_button_validate_with_exceptions(self):
        move = self.picking_with_exceptions.move_ids[0]
        move.write({"product_uom_qty": 0})
        move.write({"quantity_done": 1})
        # Result returns a dict in case it detects an exception, otherwise it returns 'True'
        result = self.picking_with_exceptions.button_validate()

        # Verify the result of the button_validate action
        # If exceptions detected, the result should be different from 'True'
        self.assertNotEqual(
            result, True, f"Expected result not to be True, but got {type(result)}"
        )

    def test_onchange_ignore_exception(self):
        # Change state and verify onchange behavior for picking
        self.picking_with_exceptions.write(
            {"state": "waiting", "ignore_exception": True}
        )
        self.assertTrue(self.picking_with_exceptions.ignore_exception)
