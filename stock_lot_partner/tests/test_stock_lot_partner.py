from odoo import fields
from odoo.tests.common import TransactionCase


class TestLotLastKnownPartner(TransactionCase):
    def setUp(self):
        super().setUp()
        # Setup a warehouse with internal location
        self.wh = self.env["stock.warehouse"].create(
            {
                "name": "Warehouse 2",
                "code": "WH2",
            }
        )
        # Create two internal sublocations under warehouse
        self.loc1 = self.env["stock.location"].create(
            {
                "name": "WH SubLoc A",
                "location_id": self.wh.view_location_id.id,
                "usage": "internal",
            }
        )
        self.loc2 = self.env["stock.location"].create(
            {
                "name": "WH SubLoc B",
                "location_id": self.wh.view_location_id.id,
                "usage": "internal",
            }
        )
        self.prod = self.env["product.product"].create(
            {
                "name": "Tracked Prod",
                "tracking": "serial",
                "type": "consu",
                "is_storable": True,
            }
        )
        self.lot = self.env["stock.lot"].create(
            {
                "name": "LOT001",
                "product_id": self.prod.id,
            }
        )
        self.supplier = self.env["res.partner"].create({"name": "Supplier X"})
        self.customer = self.env["res.partner"].create({"name": "Customer Y"})

    def test_move_into_internal_uses_warehouse_partner(self):
        # Create a move from supplier to internal location (receiving)
        move = self.env["stock.move"].create(
            {
                "product_id": self.prod.id,
                "product_uom_qty": 1,
                "product_uom": self.prod.uom_id.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.loc1.id,
                "partner_id": self.supplier.id,
                "state": "done",
                "date": fields.Datetime.now(),
            }
        )
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "lot_id": self.lot.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "product_id": self.prod.id,
                "product_uom_id": self.prod.uom_id.id,
                "quantity": 1,
            }
        )
        # Assert that partner is warehouse partner, not supplier
        self.assertEqual(
            self.lot.current_partner_id,
            self.wh.partner_id,
            "When move into internal location, warehouse partner should be used",
        )

    def test_move_to_customer_location_uses_partner(self):
        # Create a move from internal to customer location (sale delivery)
        move = self.env["stock.move"].create(
            {
                "product_id": self.prod.id,
                "product_uom_qty": 1,
                "product_uom": self.prod.uom_id.id,
                "location_id": self.loc2.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "partner_id": self.customer.id,
                "state": "done",
                "date": fields.Datetime.now(),
            }
        )
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "lot_id": self.lot.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "product_id": self.prod.id,
                "product_uom_id": self.prod.uom_id.id,
                "quantity": 1,
            }
        )
        self.assertEqual(
            self.lot.current_partner_id,
            self.customer,
            "When move to customer location, the move.partner_id should be used",
        )

    def test_move_with_source_equals_dest_ignored(self):
        # Create a move where source == dest (should be ignored)
        move = self.env["stock.move"].create(
            {
                "product_id": self.prod.id,
                "product_uom_qty": 1,
                "product_uom": self.prod.uom_id.id,
                "location_id": self.loc1.id,
                "location_dest_id": self.loc1.id,
                "partner_id": self.supplier.id,
                "state": "done",
                "date": fields.Datetime.now(),
            }
        )
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "lot_id": self.lot.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "product_id": self.prod.id,
                "product_uom_id": self.prod.uom_id.id,
                "quantity": 1,
            }
        )
        # There are no "real" moves for this lot (since only noop moves)
        # so partner should be False
        self.assertFalse(
            self.lot.current_partner_id,
            "If only moves with source == dest exist, then location_id should be False",
        )

    def test_dropship_move_uses_sale_partner(self):
        # Create a dropship picking with a sale partner
        picking_type = self.env["stock.picking.type"].search(
            [("code", "=", "dropship"), ("company_id", "=", self.env.company.id)],
            limit=1,
        )
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
            }
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "partner_id": self.customer.id,
                "is_dropship": True,
                "sale_id": sale.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "product_id": self.prod.id,
                "product_uom_qty": 1,
                "product_uom": self.prod.uom_id.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "picking_id": picking.id,
                "partner_id": self.supplier.id,
                "state": "done",
                "date": fields.Datetime.now(),
            }
        )
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "lot_id": self.lot.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "product_id": self.prod.id,
                "product_uom_id": self.prod.uom_id.id,
                "quantity": 1,
            }
        )
        # Assert that the dropship sale partner is used
        picking.sale_id = sale  # brute force for testing purpose
        self.assertEqual(
            self.lot.current_partner_id,
            self.customer,
            "For dropship moves, the picking (sale) partner must be used",
        )
