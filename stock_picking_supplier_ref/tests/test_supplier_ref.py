from odoo.tests.common import TransactionCase


class TestStockPickingSupplierReference(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        # Create a product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )

        # Create stock picking type
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

        # Create a stock picking directly
        cls.stock_picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.picking_type_out.default_location_src_id.id,
                "location_dest_id": cls.picking_type_out.default_location_dest_id.id,
            }
        )

        # Create stock move
        cls.env["stock.move"].create(
            {
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_uom_qty": 10,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.stock_picking.id,
                "location_id": cls.picking_type_out.default_location_src_id.id,
                "location_dest_id": cls.picking_type_out.default_location_dest_id.id,
            }
        )

    def test_supplier_reference_in_picking(self):
        # Set the supplier reference directly in the stock picking
        self.stock_picking.supplier_reference = "TEST-SUPPLIER-REF"

        # Ensure the supplier reference is correctly set
        self.assertEqual(
            self.stock_picking.supplier_reference,
            "TEST-SUPPLIER-REF",
            "Supplier reference should be correctly set in the stock picking",
        )

    def test_supplier_reference_field_exists(self):
        # Check if the `supplier_reference` field exists in the `stock.picking` model
        self.assertTrue(
            hasattr(self.stock_picking, "supplier_reference"),
            "Field `supplier_reference` is not present in the stock.picking model",
        )

    def test_supplier_reference_empty_by_default(self):
        # Ensure that the `supplier_reference` is empty if not explicitly set
        self.assertFalse(
            self.stock_picking.supplier_reference,
            "Field `supplier_reference` should be empty by default",
        )
