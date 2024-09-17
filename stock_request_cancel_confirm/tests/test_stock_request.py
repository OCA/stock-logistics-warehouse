from odoo.tests.common import TransactionCase


class TestStockRequest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockRequest, cls).setUpClass()
        # Create a Unit of Measure (UoM) for the product
        cls.unit_of_measure = cls.env.ref("uom.product_uom_unit").id

        # Create a test product with UoM fields
        cls.test_product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "uom_id": cls.unit_of_measure,
                "uom_po_id": cls.unit_of_measure,
            }
        )

        # Define stock request and stock request order models for easier access
        cls.StockRequest = cls.env["stock.request"]

        # Create a stock request with required fields
        cls.stock_request = cls.StockRequest.create(
            {
                "name": "Test Stock Request 1",
                "product_id": cls.test_product.id,
                "product_uom_id": cls.unit_of_measure,
                "product_uom_qty": 10,
            }
        )

        # Create a stock request order.
        cls.stock_request_order = cls.env["stock.request.order"].create(
            {
                "name": "Test Stock Request Order",
                "stock_request_ids": [0, 0, cls.stock_request.id],
            }
        )

    def test_01_stock_request_cancel_request_with_and_without_confirmation(self):
        """
        Test cancelling stock requests with and without the confirmation wizard.
        """
        # Test cancel with confirmation enabled
        self.stock_request_order.cancel_confirm = True
        stock_request_cancel = self.stock_request.action_cancel()

        self.assertEqual(
            stock_request_cancel,
            True,
            "Stock request should be cancelled directly when confirmation is enabled.",
        )
        self.assertEqual(
            self.stock_request.state,
            "cancel",
            "Stock request state should be 'cancel' when cancellation is confirmed.",
        )

        # Reset to draft and test cancel without confirmation
        self.stock_request.action_draft()
        self.stock_request_order.cancel_confirm = False
        stock_request_draft = self.stock_request.action_cancel()

        self.assertEqual(
            stock_request_draft.get("res_model"),
            "cancel.confirm",
            "Cancel confirmation wizard should be shown when confirmation is disabled.",
        )
        self.assertEqual(
            self.stock_request.state,
            "draft",
            "Stock request state should remain 'draft' when cancellation is pending "
            "confirmation.",
        )

    def test_02_stock_request_order_cancel_request_with_and_without_confirmation(self):
        """
        Test resetting stock request and stock request order to draft, and ensure
        the cancel confirmation flag is respected.
        """

        # Test draft with confirmation enabled
        self.stock_request_order.cancel_confirm = True
        stock_request_cancel = self.stock_request_order.action_cancel()

        self.assertEqual(
            stock_request_cancel,
            True,
            "Stock request order should be cancelled directly when confirmation "
            "is enabled.",
        )
        self.assertEqual(
            self.stock_request_order.state,
            "cancel",
            "Stock request order state should be 'draft' after cancellation with "
            "confirmation.",
        )

        # Reset to draft and test cancel without confirmation
        self.stock_request_order.action_draft()
        self.stock_request_order.cancel_confirm = False
        stock_request_draft = self.stock_request_order.action_cancel()

        self.assertEqual(
            stock_request_draft.get("res_model"),
            "cancel.confirm",
            "Cancel confirmation wizard should appear when confirmation is disabled "
            "for stock request order.",
        )
        self.assertEqual(
            self.stock_request_order.state,
            "draft",
            "Stock request order state should remain 'draft' when cancellation is "
            "pending confirmation.",
        )
