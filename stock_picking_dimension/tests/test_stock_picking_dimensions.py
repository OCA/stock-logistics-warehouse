from odoo.tests.common import TransactionCase


class TestStockPickingDimensions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location = cls.env["stock.location"].create(
            {"name": "Test location", "usage": "internal"}
        )
        cls.location_customers = cls.env["stock.location"].create(
            {"name": "Test location customers", "usage": "customer"}
        )
        cls.sequence = cls.env["ir.sequence"].create(
            {
                "name": "Test Sequence",
                "implementation": "standard",
                "padding": 1,
                "number_increment": 1,
            }
        )
        cls.stock_picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Test picking type",
                "code": "outgoing",
                "sequence_id": cls.sequence.id,
                "sequence_code": "test",
            }
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.stock_picking_type.id,
                "location_id": cls.location.id,
                "location_dest_id": cls.location_customers.id,
            }
        )

    def test_compute_volume(self):
        # Set dimension_uom_id to mm
        self.picking.dimension_uom_id = self.env.ref("uom.product_uom_millimeter")
        self.picking.picking_length = 1000.0
        self.picking.picking_width = 500.0
        self.picking.picking_height = 1200.0

        teoric_volume = round((1000.0 * 500.0 * 1200.0) * 0.000001, 2)

        # Set volume_uom_id to L
        self.picking.volume_uom_id = self.env.ref("uom.product_uom_litre")

        self.assertEqual(self.picking.volume, teoric_volume)

        # Change volume_uom_id to m3
        self.picking.volume_uom_id = self.env.ref("uom.product_uom_cubic_meter")
        teoric_volume = round((1000.0 * 500.0 * 1200.0) * 0.000000001, 2)
        self.assertEqual(self.picking.volume, teoric_volume)
