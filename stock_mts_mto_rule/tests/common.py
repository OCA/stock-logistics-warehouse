# Copyright 2015 Akretion
# Author: Florian da Costa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class MtoMtsRouteCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move_obj = cls.env["stock.move"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.uom = cls.env["uom.uom"].browse(1)
        cls.warehouse.mto_mts_management = True
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "consu", "is_storable": True}
        )
        cls.company_partner = cls.env.ref("base.main_partner")
        cls.group = cls.env["procurement.group"].create({"name": "test"})
        cls.procurement_vals = {"warehouse_id": cls.warehouse, "group_id": cls.group}
        cls.mto_mts_route = cls.env.ref("stock_mts_mto_rule.route_mto_mts")
        # Since mrp and purchase modules may not be installed, we need to
        # create a dummy step to show that mts, mto, and mts+mto flows work.
        # Else, if purchase/manufacture are not installed, the mto would fail.
        route_vals = {
            "warehouse_selectable": True,
            "name": "dummy route",
        }
        cls.dummy_route = cls.env["stock.route"].create(route_vals)
        rule_vals = {
            "location_dest_from_rule": True,
            "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
            "location_src_id": cls.env.ref("stock.stock_location_suppliers").id,
            "action": "pull",
            "warehouse_id": cls.warehouse.id,
            "picking_type_id": cls.env.ref("stock.picking_type_in").id,
            "name": "dummy rule",
            "route_id": cls.dummy_route.id,
        }
        cls.dummy_rule = cls.env["stock.rule"].create(rule_vals)
        cls.warehouse.write({"route_ids": [Command.link(cls.dummy_route.id)]})

    def _get_common_procurement_for_customer(self, product_qty=2.0, values=None):
        if values is None:
            values = self.procurement_vals
        return self.env["procurement.group"].Procurement(
            self.product,
            product_qty,
            self.uom,
            self.customer_loc,
            self.product.name,
            "test",
            self.warehouse.company_id,
            values,
        )

    def _create_quant(self, qty):
        self.quant = self.env["stock.quant"].create(
            {
                "owner_id": self.company_partner.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "product_id": self.product.id,
                "quantity": qty,
            }
        )
