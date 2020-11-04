# 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProcurementAutoCreateGroup(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestProcurementAutoCreateGroup, self).setUp(*args, **kwargs)
        self.group_obj = self.env["procurement.group"]
        self.push_obj = self.env["stock.rule"]
        self.route_obj = self.env["stock.location.route"]
        self.move_obj = self.env["stock.move"]
        self.picking_obj = self.env["stock.picking"]
        self.product_obj = self.env["product.product"]

        self.warehouse = self.env.ref("stock.warehouse0")
        self.location = self.env.ref("stock.stock_location_stock")
        self.company_id = self.env.ref("base.main_company")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.loc_components = self.env["stock.location"].create({"name": "TEST"})
        picking_type_id = self.env.ref("stock.picking_type_internal").id

        # Create rules and routes:
        route_auto = self.route_obj.create({"name": "Auto Create Group"})
        self.push_obj.create(
            {
                "name": "route_auto",
                "location_from_id": self.location.id,
                "location_dest_id": self.loc_components.id,
                "route_id": route_auto.id,
                "auto_create_group": True,
                "action": "push",
                "picking_type_id": picking_type_id,
                "warehouse_id": self.warehouse.id,
                "company_id": self.company_id.id,
            }
        )
        route_no_auto = self.route_obj.create({"name": "Not Auto Create Group"})
        self.push_obj.create(
            {
                "name": "route_no_auto",
                "location_from_id": self.location.id,
                "location_dest_id": self.loc_components.id,
                "route_id": route_no_auto.id,
                "auto_create_group": False,
                "action": "push",
                "picking_type_id": picking_type_id,
                "warehouse_id": self.warehouse.id,
                "company_id": self.company_id.id,
            }
        )

        # Prepare products:
        self.prod_auto = self.product_obj.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "route_ids": [(6, 0, [route_auto.id])],
            }
        )
        self.prod_no_auto = self.product_obj.create(
            {
                "name": "Test Product 2",
                "type": "product",
                "route_ids": [(6, 0, [route_no_auto.id])],
            }
        )

    def _push_trigger(self, product):
        picking = self.picking_obj.create(
            {
                "picking_type_id": self.ref("stock.picking_type_in"),
                "location_id": self.supplier_location.id,
                "location_dest_id": self.location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": product.id,
                            "date_expected": "2099-06-01 18:00:00",
                            "date": "2099-06-01 18:00:00",
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.location.id,
                        },
                    )
                ],
            }
        )
        picking.force_assign()
        picking.move_lines.write({"quantity_done": 1.0})
        picking.button_validate()

    def test_01_no_auto_create_group(self):
        """Test no auto creation of group."""
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_no_auto.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertFalse(move)
        self._push_trigger(self.prod_no_auto)
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_no_auto.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertTrue(move)
        self.assertFalse(
            move.group_id, "Procurement Group should not have been assigned."
        )

    def test_02_auto_create_group(self):
        """Test auto creation of group."""
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_auto.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertFalse(move)
        self._push_trigger(self.prod_auto)
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_auto.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertTrue(move)
        self.assertTrue(move.group_id, "Procurement Group not assigned.")
