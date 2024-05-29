# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
from odoo.tests.common import SavepointCase


class TestMtoMtsRouteCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move_obj = cls.env["stock.move"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.uom = cls.env["uom.uom"].browse(1)
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "product"}
        )
        cls.company_partner = cls.env.ref("base.main_partner")
        cls.group = cls.env["procurement.group"].create({"name": "test"})

    @classmethod
    def setUpRules(cls):
        cls.warehouse.mto_mts_management = True
        cls.procurement_vals = {"warehouse_id": cls.warehouse, "group_id": cls.group}
        # Since mrp and purchase modules may not be installed, we need to
        # create a dummy step to show that mts, mto, and mts+mto flows work.
        # Else, if purchase/manufacture are not installed, the mto would fail.
        route_vals = {
            "warehouse_selectable": True,
            "name": "dummy route",
        }
        cls.dummy_route = cls.env["stock.location.route"].create(route_vals)
        rule_vals = {
            "location_id": cls.env.ref("stock.stock_location_stock").id,
            "location_src_id": cls.env.ref("stock.stock_location_suppliers").id,
            "action": "pull",
            "warehouse_id": cls.warehouse.id,
            "picking_type_id": cls.env.ref("stock.picking_type_out").id,
            "name": "dummy rule",
            "route_id": cls.dummy_route.id,
        }
        cls.dummy_rule = cls.env["stock.rule"].create(rule_vals)
        cls.warehouse.write({"route_ids": [(4, cls.dummy_route.id)]})

    @classmethod
    def _create_quant(cls, qty):
        cls.quant = cls.env["stock.quant"].create(
            {
                "owner_id": cls.company_partner.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "product_id": cls.product.id,
                "quantity": qty,
            }
        )

    @classmethod
    def _run_procurement(cls, qty):
        cls.env["procurement.group"].run(
            [
                cls.group.Procurement(
                    cls.product,
                    qty,
                    cls.uom,
                    cls.customer_loc,
                    cls.product.name,
                    "test",
                    cls.warehouse.company_id,
                    cls.procurement_vals,
                )
            ]
        )
        return cls.move_obj.search([("group_id", "=", cls.group.id)])
