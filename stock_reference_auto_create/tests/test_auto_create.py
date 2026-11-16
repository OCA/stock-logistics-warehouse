# Copyright 2017-2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockReferenceAutoCreate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.reference_obj = cls.env["stock.reference"]
        cls.rule_obj = cls.env["stock.rule"]
        cls.route_obj = cls.env["stock.route"]
        cls.move_obj = cls.env["stock.move"]
        cls.picking_obj = cls.env["stock.picking"]
        cls.product_obj = cls.env["product.product"]

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location = cls.warehouse.lot_stock_id
        cls.company_id = cls.warehouse.company_id
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.loc_components = cls.env["stock.location"].create(
            {
                "name": "Components",
                "usage": "internal",
                "location_id": cls.warehouse.view_location_id.id,
            }
        )
        picking_type_id = cls.warehouse.int_type_id.id

        cls.partner = cls.env["res.partner"].create({"name": "Partner"})

        # Create rules and routes:
        pull_push_route_auto = cls.route_obj.create({"name": "Auto Create Group"})
        cls.pull_push_rule_auto = cls.rule_obj.create(
            {
                "name": "rule with autocreate",
                "route_id": pull_push_route_auto.id,
                "auto_create_reference": True,
                "action": "pull_push",
                "warehouse_id": cls.warehouse.id,
                "picking_type_id": picking_type_id,
                "location_dest_id": cls.location.id,
                "location_src_id": cls.loc_components.id,
                "partner_address_id": cls.partner.id,
            }
        )
        pull_push_route_no_auto = cls.route_obj.create(
            {"name": "Not Auto Create Group"}
        )
        cls.rule_obj.create(
            {
                "name": "rule with no autocreate",
                "route_id": pull_push_route_no_auto.id,
                "auto_create_reference": False,
                "action": "pull_push",
                "warehouse_id": cls.warehouse.id,
                "picking_type_id": picking_type_id,
                "location_dest_id": cls.location.id,
                "location_src_id": cls.loc_components.id,
            }
        )
        push_route_auto = cls.route_obj.create({"name": "Auto Create Group"})
        cls.push_rule_auto = cls.rule_obj.create(
            {
                "name": "route_auto",
                "location_src_id": cls.location.id,
                "location_dest_id": cls.loc_components.id,
                "route_id": push_route_auto.id,
                "auto_create_reference": True,
                "auto": "manual",
                "picking_type_id": picking_type_id,
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.company_id.id,
                "action": "push",
            }
        )
        push_route_no_auto = cls.route_obj.create({"name": "Not Auto Create Group"})
        cls.rule_obj.create(
            {
                "name": "route_no_auto",
                "location_src_id": cls.location.id,
                "location_dest_id": cls.loc_components.id,
                "route_id": push_route_no_auto.id,
                "auto_create_reference": False,
                "auto": "manual",
                "picking_type_id": picking_type_id,
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.company_id.id,
                "action": "push",
            }
        )

        # Prepare products:
        cls.prod_auto_pull_push = cls.product_obj.create(
            {
                "name": "Test Product 1",
                "is_storable": True,
                "route_ids": [(6, 0, [pull_push_route_auto.id])],
            }
        )
        cls.prod_no_auto_pull_push = cls.product_obj.create(
            {
                "name": "Test Product 2",
                "is_storable": True,
                "route_ids": [(6, 0, [pull_push_route_no_auto.id])],
            }
        )
        cls.prod_auto_push = cls.product_obj.create(
            {
                "name": "Test Product 3",
                "is_storable": True,
                "route_ids": [(6, 0, [push_route_auto.id])],
            }
        )
        cls.prod_no_auto_push = cls.product_obj.create(
            {
                "name": "Test Product 4",
                "is_storable": True,
                "route_ids": [(6, 0, [push_route_no_auto.id])],
            }
        )

        cls.reference = cls.reference_obj.create({"name": "SO0001"})

    @classmethod
    def _procure(cls, product):
        values = {
            "reference_ids": cls.reference,
        }
        cls.rule_obj.run(
            [
                cls.rule_obj.Procurement(
                    product,
                    5.0,
                    product.uom_id,
                    cls.location,
                    "TEST",
                    "odoo tests",
                    cls.env.company,
                    values,
                )
            ]
        )
        return True

    @classmethod
    def _push_trigger(cls, product):
        picking = cls.picking_obj.create(
            {
                "picking_type_id": cls.warehouse.in_type_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "date_deadline": "2099-06-01 18:00:00",
                            "date": "2099-06-01 18:00:00",
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": 1.0,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.location.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.move_ids.write({"quantity": 1.0})
        picking.button_validate()

    def test_01_pull_push_no_auto_create_reference(self):
        """Test auto creation of reference."""
        move = self.move_obj.search(
            [("product_id", "=", self.prod_no_auto_pull_push.id)]
        )
        self.assertFalse(move)
        self._procure(self.prod_no_auto_pull_push)
        move = self.move_obj.search(
            [("product_id", "=", self.prod_no_auto_pull_push.id)]
        )
        self.assertTrue(move)
        self.assertEqual(
            move.reference_ids,
            self.reference,
            "Reference should not have been auto-created.",
        )

    def test_02_pull_push_auto_create_reference(self):
        move = self.move_obj.search([("product_id", "=", self.prod_auto_pull_push.id)])
        self.assertFalse(move)
        self._procure(self.prod_auto_pull_push)
        move = self.move_obj.search([("product_id", "=", self.prod_auto_pull_push.id)])
        self.assertTrue(move)
        self.assertTrue(move.reference_ids, "Reference not assigned.")
        self.assertNotEqual(move.reference_ids, self.reference)
        self.assertTrue(move.reference_ids.name.startswith("SR/"))
        self.assertEqual(move.partner_id, self.partner)

    def test_04_push_no_auto_create_reference(self):
        """Test no auto creation of reference."""
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_no_auto_push.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertFalse(move)
        self._push_trigger(self.prod_no_auto_push)
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_no_auto_push.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertTrue(move)
        self.assertFalse(move.reference_ids, "Reference should not have been assigned.")

    def test_05_push_auto_create_reference(self):
        """Test auto creation of reference."""
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_auto_push.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertFalse(move)
        self._push_trigger(self.prod_auto_push)
        move = self.move_obj.search(
            [
                ("product_id", "=", self.prod_auto_push.id),
                ("location_dest_id", "=", self.loc_components.id),
            ]
        )
        self.assertTrue(move)
        self.assertTrue(move.reference_ids, "Reference not assigned.")
