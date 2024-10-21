# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests.common import Form

from odoo.addons.base.tests.common import BaseCommon


class TestStockSafeScrap(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("stock.group_stock_multi_locations")
        cls.env.user.groups_id += cls.env.ref("stock.group_stock_manager")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.type_out = cls.env.ref("stock.picking_type_out")
        cls.owner = cls.env["res.partner"].create(
            {
                "name": "Test Owner",
            }
        )
        cls.shelf_test = cls.env["stock.location"].create(
            {
                "name": "Shelf Test",
                "location_id": cls.env.ref("stock.stock_location_stock").id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test product 2",
                "type": "product",
            }
        )

    def _create_quantity(self, **kwargs):
        values = {
            "location_id": self.shelf_test.id,
            "product_id": self.product.id,
            "inventory_quantity": 10.0,
        }
        values.update(kwargs)
        quant = self.env["stock.quant"].with_context(inventory_mode=True).create(values)
        quant._apply_inventory()
        return quant

    def _create_picking(self, **kwargs):
        values = {
            "picking_type_id": self.type_out.id,
            "location_id": self.shelf_test.id,
            "location_dest_id": self.customers.id,
            "move_ids": [
                Command.create(
                    {
                        "name": self.product.id,
                        "location_id": self.shelf_test.id,
                        "location_dest_id": self.customers.id,
                        "product_id": self.product.id,
                        "product_uom_qty": 10.0,
                        "product_uom": self.product.uom_id.id,
                    }
                )
            ],
        }
        values.update(kwargs)
        self.picking = self.env["stock.picking"].create(values)
        return self.picking

    def _create_scrap(self, **kwargs):
        with Form(self.env["stock.scrap"]) as scrap_form:
            scrap_form.location_id = self.shelf_test
            scrap_form.product_id = self.product
        scrap = scrap_form.save()
        for k_arg, value in kwargs.items():
            scrap[k_arg] = value
        return scrap

    def _create_package(self, quant_ids, **kwargs):
        values = {
            "quant_ids": [Command.set(quant_ids)],
        }
        values.update(kwargs)
        return self.env["stock.quant.package"].create(values)

    def test_stock_scrap(self):
        # Set stock quantities for both products
        # Create a picking and fill in the done quantity
        # Create a first scrap
        # Create a second scrap with the product 2
        # Only the first scrap should fail
        self._create_quantity()
        self._create_quantity(product_id=self.product_2.id)
        self._create_picking()
        self.picking.action_confirm()
        self.picking.action_assign()

        # Picking operation in progress
        self.picking.move_line_ids.qty_done = 10.0
        scrap = self._create_scrap()
        self.product = self.product_2
        scrap2 = self._create_scrap()
        pickings = (scrap | scrap2).mapped("in_progress_picking_ids")
        self.assertEqual(self.picking, pickings)
        self.assertEqual(self.picking, scrap.in_progress_picking_ids)
        self.assertFalse(scrap2.in_progress_picking_ids)
        with self.assertRaises(UserError) as exc:
            scrap.do_scrap()
        picking_name = self.picking.name
        self.assertEqual(
            "Some picking operations are in progress. You cannot do a scrap at the same time."
            f" \n\nPickings concerned: {picking_name}",
            exc.exception.args[0],
        )
        scrap2.do_scrap()

    def test_stock_scrap_owner_no_progress(self):
        # Set stock quantities for both products
        # Create a picking and fill in the done quantity
        # Create a first scrap
        # Create a second scrap with the product 2
        # Only the first scrap should fail
        self._create_quantity(owner_id=self.owner.id)
        self._create_quantity(product_id=self.product_2.id)
        self._create_picking()
        self.picking.action_confirm()
        self.picking.action_assign()

        # Picking operation in progress
        self.picking.move_line_ids.qty_done = 10.0
        scrap = self._create_scrap()
        self.product = self.product_2
        scrap2 = self._create_scrap()
        pickings = (scrap | scrap2).mapped("in_progress_picking_ids")
        self.assertFalse(pickings)
        self.assertFalse(scrap.in_progress_picking_ids)
        self.assertFalse(scrap2.in_progress_picking_ids)

    def test_stock_scrap_owner(self):
        # Create a scrap with an owner
        self._create_quantity(owner_id=self.owner.id)
        picking = self._create_picking(owner_id=self.owner.id)
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids.qty_done = 10.0
        scrap = self._create_scrap(owner_id=self.owner.id)
        self.assertEqual(picking, scrap.in_progress_picking_ids)

    def test_stock_scrap_package(self):
        # Create a scrap with a package
        quant = self._create_quantity()
        package = self._create_package(quant_ids=quant.ids)
        picking = self._create_picking()
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids.qty_done = 10.0
        scrap = self._create_scrap(package_id=package.id)
        self.assertEqual(picking, scrap.in_progress_picking_ids)

    def test_stock_scrap_lot(self):
        # Create a scrap with a lot
        lot = self.env["stock.lot"].create(
            {
                "name": "Test",
                "product_id": self.product.id,
            }
        )
        self._create_quantity(lot_id=lot.id)
        picking = self._create_picking()
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids.qty_done = 10.0
        scrap = self._create_scrap(lot_id=lot.id)
        self.assertEqual(picking, scrap.in_progress_picking_ids)
