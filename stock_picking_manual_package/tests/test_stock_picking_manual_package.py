# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
    def setUp(self):
        super(TestStockPicking, self).setUp()

        # models
        self.picking_model = self.env["stock.picking"]

        # warehouse and picking types
        self.warehouse = self.env.ref("stock.stock_warehouse_shop0")
        self.picking_type_in = self.env.ref("stock.chi_picking_type_in")
        self.picking_type_out = self.env.ref("stock.chi_picking_type_out")
        self.picking_type_in.show_reserved = True
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.stock_location = self.warehouse.lot_stock_id

        # Allow all companies for OdooBot user and set default user company
        # to warehouse company
        companies = self.env["res.company"].search([])
        self.env.user.company_ids = [(6, 0, companies.ids)]
        self.env.user.company_id = self.warehouse.company_id

        # products
        self.product_8 = self.env.ref("product.product_product_8")
        self.product_9 = self.env.ref("product.product_product_9")
        self.product_10 = self.env.ref("product.product_product_10")
        product_list = [self.product_8, self.product_9, self.product_10]

        # Supplier
        self.customer = self.env.ref("base.res_partner_12")

        picking_form = Form(
            self.picking_model.with_context(
                default_picking_type_id=self.picking_type_in.id
            )
        )
        picking_form.picking_type_id = self.picking_type_in
        picking_form.location_id = self.supplier_location
        picking_form.location_dest_id = self.stock_location
        for product in product_list:
            with picking_form.move_ids_without_package.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = 5
        self.picking_in = picking_form.save()

    def test_manual_package(self):
        self.picking_in.action_assign()
        # Add done quantities
        for line in self.picking_in.move_line_ids:
            line.qty_done = line.product_uom_qty
        action = self.picking_in.with_context(test_manual_package=True).put_in_pack()
        self.assertEqual(action["res_model"], "stock.picking.manual.package.wiz")
        wiz = self.env["stock.picking.manual.package.wiz"].browse(action["res_id"])
        wiz.package_id = self.env["stock.quant.package"].create({"name": "TEST-0001"})
        package = wiz.action_confirm()
        self.assertEqual(package, wiz.package_id)
        packages = self.picking_in.move_line_ids.mapped("result_package_id")
        self.assertEqual(len(packages), 1)

    def test_manual_package_with_n_lines(self):
        self.picking_in.action_assign()
        # Add done quantities
        for line in self.picking_in.move_line_ids:
            line.qty_done = line.product_uom_qty
        action = self.picking_in.with_context(test_manual_package=True).put_in_pack()
        wiz = self.env["stock.picking.manual.package.wiz"].browse(action["res_id"])
        wiz.package_id = self.env["stock.quant.package"].create({"name": "TEST-0001"})
        wiz.nbr_lines_into_package = 1
        wiz.action_confirm()
        packages = self.picking_in.move_line_ids.mapped("result_package_id")
        self.assertEqual(len(packages), 1)
