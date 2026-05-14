# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestStockLotWarranty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]
        cls.Lot = cls.env["stock.lot"]
        cls.Partner = cls.env["res.partner"]
        cls.Picking = cls.env["stock.picking"]
        cls.Move = cls.env["stock.move"]
        cls.MoveLine = cls.env["stock.move.line"]
        cls.Uom = cls.env.ref("uom.product_uom_unit")
        cls.StockLocation = cls.env["stock.location"]
        cls.SupplierInfo = cls.env["product.supplierinfo"]

        cls.partner = cls.Partner.create({"name": "Test Partner"})
        cls.stock_loc = cls.StockLocation.search([("usage", "=", "internal")], limit=1)
        cls.customer_loc = cls.StockLocation.search(
            [("usage", "=", "customer")], limit=1
        )
        cls.supplier_loc = cls.StockLocation.search(
            [("usage", "=", "supplier")], limit=1
        )

        cls.product_serial = cls.Product.create(
            {
                "name": "Serial Product",
                "type": "consu",
                "tracking": "serial",
                "uom_id": cls.Uom.id,
                "warranty": 12,
                "warranty_type": "month",
            }
        )

        cls.product_lot = cls.Product.create(
            {
                "name": "Lot Product",
                "type": "consu",
                "tracking": "lot",
                "uom_id": cls.Uom.id,
                "warranty": 6,
                "warranty_type": "month",
            }
        )

        cls.lot_serial = cls.Lot.create(
            {
                "product_id": cls.product_serial.id,
                "name": "SN0001",
            }
        )

        cls.lot_lot = cls.Lot.create(
            {
                "product_id": cls.product_lot.id,
                "name": "LOT0001",
            }
        )

        cls.SupplierInfo.create(
            {
                "product_tmpl_id": cls.product_serial.product_tmpl_id.id,
                "partner_id": cls.partner.id,
                "min_qty": 0,
                "price": 10.0,
                "warranty_duration": 18,
            }
        )

        cls.SupplierInfo.create(
            {
                "product_tmpl_id": cls.product_serial.product_tmpl_id.id,
                "partner_id": cls.partner.id,
                "min_qty": 10,
                "price": 5.0,
                "warranty_duration": 19,
            }
        )

    def test_compute_warranty_end_date(self):
        start_date = date(2026, 1, 1)
        end_date = self.lot_serial._compute_warranty_end_date(start_date, 12, "month")
        self.assertEqual(end_date, date(2027, 1, 1))
        self.assertFalse(
            self.lot_serial._compute_warranty_end_date(start_date, 0, "month")
        )

    def test_set_customer_warranty(self):
        start_date = date(2026, 1, 1)
        self.lot_serial._set_customer_warranty(start_date)
        self.assertEqual(self.lot_serial.customer_warranty_start_date, start_date)
        expected_end = date(2027, 1, 1)
        self.assertEqual(self.lot_serial.customer_warranty_end_date, expected_end)

    def test_set_vendor_warranty(self):
        start_date = date(2026, 1, 1)
        self.lot_serial._set_vendor_warranty(
            start_date, vendor=self.partner, quantity=1
        )
        self.assertEqual(self.lot_serial.vendor_warranty_start_date, start_date)
        self.assertEqual(self.lot_serial.vendor_warranty_end_date, date(2027, 7, 1))
        self.lot_serial._set_vendor_warranty(
            start_date, vendor=self.partner, quantity=11
        )
        self.assertEqual(self.lot_serial.vendor_warranty_end_date, date(2027, 8, 1))

    def test_update_and_reset_customer_warranty(self):
        picking = self.Picking.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.customer_loc.id,
            }
        )
        move = self.Move.create(
            {
                "product_id": self.product_serial.id,
                "product_uom_qty": 1,
                "product_uom": self.Uom.id,
                "picking_id": picking.id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.customer_loc.id,
            }
        )
        date = fields.Date.context_today(self)
        move_line = self.MoveLine.create(
            {
                "move_id": move.id,
                "product_id": self.product_serial.id,
                "lot_id": self.lot_serial.id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.customer_loc.id,
                "quantity": 1,
                "date": date,
            }
        )

        move_line._action_done()
        self.assertEqual(self.lot_serial.customer_warranty_start_date, date)
        self.assertEqual(
            self.lot_serial.customer_warranty_end_date,
            date + relativedelta(**{"months": 12}),
        )

        picking = self.Picking.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.customer_loc.id,
                "location_dest_id": self.stock_loc.id,
            }
        )
        move = self.Move.create(
            {
                "product_id": self.product_serial.id,
                "product_uom_qty": 1,
                "product_uom": self.Uom.id,
                "picking_id": picking.id,
                "location_id": self.customer_loc.id,
                "location_dest_id": self.stock_loc.id,
            }
        )
        date = fields.Date.context_today(self)
        move_line = self.MoveLine.create(
            {
                "move_id": move.id,
                "product_id": self.product_serial.id,
                "lot_id": self.lot_serial.id,
                "location_id": self.customer_loc.id,
                "location_dest_id": self.stock_loc.id,
                "quantity": 1,
                "date": date,
            }
        )
        move_line._action_done()
        self.assertFalse(self.lot_serial.customer_warranty_start_date)
        self.assertFalse(self.lot_serial.customer_warranty_end_date)

    def test_update_and_reset_vendor_warranty(self):
        picking = self.Picking.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.supplier_loc.id,
                "location_dest_id": self.stock_loc.id,
            }
        )
        move = self.Move.create(
            {
                "product_id": self.product_serial.id,
                "product_uom_qty": 1,
                "product_uom": self.Uom.id,
                "picking_id": picking.id,
                "location_id": self.supplier_loc.id,
                "location_dest_id": self.stock_loc.id,
            }
        )
        date = fields.Date.context_today(self)
        move_line = self.MoveLine.create(
            {
                "move_id": move.id,
                "product_id": self.product_serial.id,
                "lot_id": self.lot_serial.id,
                "location_id": self.supplier_loc.id,
                "location_dest_id": self.stock_loc.id,
                "quantity": 1,
                "date": date,
            }
        )

        move_line._action_done()
        self.assertEqual(self.lot_serial.vendor_warranty_start_date, date)
        self.assertEqual(
            self.lot_serial.vendor_warranty_end_date,
            date + relativedelta(**{"months": 18}),
        )

        picking = self.Picking.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.supplier_loc.id,
            }
        )
        move = self.Move.create(
            {
                "product_id": self.product_serial.id,
                "product_uom_qty": 1,
                "product_uom": self.Uom.id,
                "picking_id": picking.id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.supplier_loc.id,
            }
        )
        date = fields.Date.context_today(self)
        move_line = self.MoveLine.create(
            {
                "move_id": move.id,
                "product_id": self.product_serial.id,
                "lot_id": self.lot_serial.id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.supplier_loc.id,
                "quantity": 1,
                "date": date,
            }
        )
        move_line._action_done()
        self.assertFalse(self.lot_serial.vendor_warranty_start_date)
        self.assertFalse(self.lot_serial.vendor_warranty_end_date)

    def test_serial_only_logic(self):
        # Non-serial product should skip warranty on _action_done
        picking = self.Picking.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.customer_loc.id,
            }
        )
        move = self.Move.create(
            {
                "product_id": self.product_lot.id,
                "product_uom_qty": 1,
                "product_uom": self.Uom.id,
                "picking_id": picking.id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.customer_loc.id,
            }
        )
        move_line = self.MoveLine.create(
            {
                "move_id": move.id,
                "product_id": self.product_lot.id,
                "lot_id": self.lot_lot.id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.customer_loc.id,
                "quantity": 1,
                "date": fields.Date.context_today(self),
            }
        )

        move_line._action_done()
        self.assertFalse(self.lot_lot.customer_warranty_start_date)
        self.assertFalse(self.lot_lot.customer_warranty_end_date)
