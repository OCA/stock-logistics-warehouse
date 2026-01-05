from odoo.tests import Form, TransactionCase, tagged


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
                "is_storable": True,
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

        cls.env.user.groups_id += cls.env.ref("stock.group_tracking_lot")

    def test_autoload_package(self):
        picking_f = Form(self.StockPicking)
        picking_f.partner_id = self.env.ref("base.res_partner_address_15")
        picking_f.picking_type_id = self.env.ref("stock.picking_type_out")
        with picking_f.move_ids_without_package.new() as move_f:
            move_f.product_id = self.product
            move_f.product_uom_qty = 3.0

        picking_to_package = picking_f.save()
        picking_to_package.action_confirm()
        move = picking_to_package.move_ids_without_package
        package_domain = self.StockQuantPackage.search(move._package_domain())
        self.assertEqual(package_domain, self.package)

        with Form(
            move[0],
            view=self.env.ref("stock_package_autoload.view_stock_move_operations"),
        ) as move_f:
            move_f.load_products_from_package_id = self.package

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
        with Form(
            move[0],
            view=self.env.ref("stock_package_autoload.view_stock_move_operations"),
        ) as move_f:
            move_f.load_products_from_package_id = self.package

        self.assertEqual(n_move_lines, len(move.move_line_ids))
        self.assertEqual(
            move.move_line_ids.mapped("lot_id"), self.package.quant_ids.mapped("lot_id")
        )
