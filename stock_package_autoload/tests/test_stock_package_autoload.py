from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockPackageAutoload(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env["product.product"]
        cls.StockMove = cls.env["stock.move"]
        cls.StockMoveLine = cls.env["stock.move.line"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.StockProductionLot = cls.env["stock.lot"]
        cls.StockQuantPackage = cls.env["stock.quant.package"]

        cls.company = cls.env.company
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.location_dest = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.ProductProduct.create(
            {
                "name": "Test Product With Serial",
                "type": "product",
                "tracking": "serial",
            }
        )

        n_lots = 6
        cls.lots = cls.StockProductionLot.create(
            [
                {
                    "name": "0" * 4 + str(i),
                    "product_id": cls.product.id,
                    "company_id": cls.company.id,
                }
                for i in range(1, n_lots + 1)
            ]
        )

        cls.package = cls.StockQuantPackage.create(
            {
                "name": "PACK000014",
                "quant_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "product_uom_id": cls.uom_unit,
                            "location_id": cls.location.id,
                            "lot_id": lot.id,
                        },
                    )
                    for lot in cls.lots[:3]
                ],
            }
        )

    def test_autoload_package(self):
        picking_to_package = self.StockPicking.create(
            {
                "partner_id": self.env.ref("base.res_partner_address_15").id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.location.id,
                "location_dest_id": self.location_dest.id,
                "company_id": self.company.id,
                "move_line_ids_without_package": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "reserved_uom_qty": 3,
                            "product_uom_id": self.uom_unit.id,
                            "location_id": self.location.id,
                            "location_dest_id": self.location_dest.id,
                            "company_id": self.env.company.id,
                        },
                    )
                ],
            }
        )
        picking_to_package.action_confirm()
        move = picking_to_package.move_ids_without_package
        package_domain = self.StockQuantPackage.search(move._package_domain())
        self.assertEqual(package_domain, self.package)
        move.load_products_from_package_id = self.package
        move._onchange_load_products_from_package_id()
        self.assertFalse(move.load_products_from_package_id)
        n_move_lines = len(move.move_line_ids)
        self.assertEqual(
            move.move_line_ids.mapped("lot_id"), self.package.quant_ids.mapped("lot_id")
        )
        # delete a line
        move.move_line_ids[1].unlink()
        self.assertNotEqual(
            move.move_line_ids.mapped("lot_id"), self.package.quant_ids.mapped("lot_id")
        )
        self.assertLess(len(move.move_line_ids), n_move_lines)
        # by selecting the same package again, only the missing serial will be added to
        # the move lines
        move.load_products_from_package_id = self.package
        move._onchange_load_products_from_package_id()
        self.assertEqual(n_move_lines, len(move.move_line_ids))
        self.assertEqual(
            move.move_line_ids.mapped("lot_id"), self.package.quant_ids.mapped("lot_id")
        )
