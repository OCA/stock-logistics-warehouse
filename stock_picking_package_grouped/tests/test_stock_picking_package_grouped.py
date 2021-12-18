# Copyright 2021 Tecnativa - Sergio Teruel
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
        self.picking_type_out = self.env.ref("stock.chi_picking_type_out")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")

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

        # customer
        self.customer = self.env.ref("base.res_partner_12")

        picking_form = Form(
            self.picking_model.with_context(
                default_picking_type_id=self.picking_type_out.id
            )
        )
        picking_form.partner_id = self.customer
        picking_form.picking_type_id = self.picking_type_out
        picking_form.location_id = self.picking_type_out.default_location_src_id
        picking_form.location_dest_id = self.customer_location
        for product in product_list:
            with picking_form.move_ids_without_package.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = 1
        self.picking_out = picking_form.save()

    def test_no_value_selected(self):
        self.picking_out.action_assign()
        # Add done quantities
        for line in self.picking_out.move_lines:
            line.quantity_done = line.product_uom_qty
        self.picking_out.picking_type_id.package_grouping = False
        self.picking_out.put_in_pack()
        packages = self.picking_out.mapped("move_line_ids.result_package_id")
        self.assertEqual(len(packages), 1)

    def test_one_package_per_detailed_operation_line(self):
        self.picking_out.action_assign()
        # Add done quantities
        for line in self.picking_out.move_lines:
            line.quantity_done = line.product_uom_qty
        self.picking_out.picking_type_id.package_grouping = "line"
        self.picking_out.put_in_pack()
        packages = self.picking_out.mapped("move_line_ids.result_package_id")
        self.assertEqual(len(packages), 3)

    def test_one_package_per_all_detailed_operation_line(self):
        self.picking_out.action_assign()
        # Add done quantities
        for line in self.picking_out.move_lines:
            line.quantity_done = line.product_uom_qty
        self.picking_out.picking_type_id.package_grouping = "standard"
        self.picking_out.put_in_pack()
        packages = self.picking_out.mapped("move_line_ids.result_package_id")
        self.assertEqual(len(packages), 1)
