# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class ReservationRateCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Location = cls.env["stock.location"]
        cls.PickingType = cls.env["stock.picking.type"]
        cls.Route = cls.env["stock.route"]
        cls.Product = cls.env["product.product"]
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"

        cls.out = cls.warehouse.wh_output_stock_loc_id
        # Use a pick ship process
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.location_a = cls.Location.create(
            {
                "name": "A",
                "location_id": cls.stock.id,
                "usage": "view",
            }
        )
        cls.location_a_1 = cls.Location.create(
            {
                "name": "A1",
                "location_id": cls.location_a.id,
                "usage": "internal",
            }
        )

        cls.location_b = cls.Location.create(
            {
                "name": "B",
                "location_id": cls.stock.id,
                "usage": "view",
            }
        )
        cls.location_b_1 = cls.Location.create(
            {
                "name": "B1",
                "location_id": cls.location_b.id,
                "usage": "internal",
            }
        )
        cls.location_c = cls.Location.create(
            {
                "name": "C",
                "location_id": cls.stock.id,
                "usage": "view",
            }
        )
        cls.location_c_1 = cls.Location.create(
            {
                "name": "C1",
                "location_id": cls.location_c.id,
                "usage": "internal",
            }
        )
        # Create picking types for zones
        cls.picking_type_a = cls.PickingType.create(
            {
                "name": "Zone A",
                "default_location_src_id": cls.location_a.id,
                "default_location_dest_id": cls.out.id,
                "sequence_code": "PICKA",
            }
        )
        cls.picking_type_b = cls.PickingType.create(
            {
                "name": "Zone B",
                "default_location_src_id": cls.location_b.id,
                "default_location_dest_id": cls.out.id,
                "sequence_code": "PICKB",
            }
        )
        cls.picking_type_c = cls.PickingType.create(
            {
                "name": "Zone C",
                "default_location_src_id": cls.location_c.id,
                "default_location_dest_id": cls.out.id,
                "sequence_code": "PICKC",
            }
        )

        cls.route_a = cls.Route.create(
            {
                "name": "Zone A",
                "rule_ids": [
                    Command.create(
                        {
                            "name": "A > OUT",
                            "action": "pull",
                            "location_dest_id": cls.out.id,
                            "location_src_id": cls.location_a.id,
                            "procure_method": "make_to_stock",
                            "picking_type_id": cls.picking_type_a.id,
                        }
                    ),
                    Command.create(
                        {
                            "name": "OUT > Sortie",
                            "action": "pull",
                            "location_dest_id": cls.customers.id,
                            "location_src_id": cls.out.id,
                            "procure_method": "make_to_order",
                            "picking_type_id": cls.warehouse.out_type_id.id,
                        }
                    ),
                ],
            }
        )
        cls.route_b = cls.Route.create(
            {
                "name": "Zone B",
                "rule_ids": [
                    Command.create(
                        {
                            "name": "B > OUT",
                            "action": "pull",
                            "location_dest_id": cls.out.id,
                            "location_src_id": cls.location_b.id,
                            "procure_method": "make_to_stock",
                            "picking_type_id": cls.picking_type_b.id,
                        }
                    ),
                    Command.create(
                        {
                            "name": "OUT > Sortie",
                            "action": "pull",
                            "location_dest_id": cls.customers.id,
                            "location_src_id": cls.out.id,
                            "procure_method": "make_to_order",
                            "picking_type_id": cls.warehouse.out_type_id.id,
                        }
                    ),
                ],
            }
        )
        cls.route_c = cls.Route.create(
            {
                "name": "Zone C",
                "rule_ids": [
                    Command.create(
                        {
                            "name": "C > OUT",
                            "action": "pull",
                            "location_dest_id": cls.out.id,
                            "location_src_id": cls.location_c.id,
                            "procure_method": "make_to_stock",
                            "picking_type_id": cls.picking_type_c.id,
                        }
                    ),
                    Command.create(
                        {
                            "name": "OUT > Sortie",
                            "action": "pull",
                            "location_dest_id": cls.customers.id,
                            "location_src_id": cls.out.id,
                            "procure_method": "make_to_order",
                            "picking_type_id": cls.warehouse.out_type_id.id,
                        }
                    ),
                ],
            }
        )
        cls.product_a = cls.Product.create(
            {
                "name": "Product A",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.set(cls.route_a.ids)],
            }
        )
        cls.product_b = cls.Product.create(
            {
                "name": "Product B",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.set(cls.route_b.ids)],
            }
        )
        cls.product_c = cls.Product.create(
            {
                "name": "Product C",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.set(cls.route_c.ids)],
            }
        )
        cls.products = cls.product_a | cls.product_b | cls.product_c

        # Procurement group
        cls.group = cls.env["procurement.group"].create({"name": "TEST"})

    @classmethod
    def _set_inventory(cls):
        Quant = cls.env["stock.quant"].with_context(inventory_mode=True)
        Quant.create(
            {
                "location_id": cls.location_a_1.id,
                "product_id": cls.product_a.id,
                "inventory_quantity": 50.0,
            }
        )._apply_inventory()
        Quant.create(
            {
                "location_id": cls.location_b_1.id,
                "product_id": cls.product_b.id,
                "inventory_quantity": 5.0,
            }
        )._apply_inventory()
        Quant.create(
            {
                "location_id": cls.location_c_1.id,
                "product_id": cls.product_c.id,
                "inventory_quantity": 0.0,
            }
        )._apply_inventory()

    @classmethod
    def _run_procurements(cls):
        cls.env["procurement.group"].run(
            [
                cls.env["procurement.group"].Procurement(
                    cls.product_a,
                    10.0,
                    cls.product_a.uom_id,
                    cls.customers,
                    "Test A",
                    "Test A",
                    cls.env.company,
                    {"partner_id": cls.partner.id, "group_id": cls.group},
                ),
                cls.env["procurement.group"].Procurement(
                    cls.product_b,
                    10.0,
                    cls.product_b.uom_id,
                    cls.customers,
                    "Test B",
                    "Test B",
                    cls.env.company,
                    {"partner_id": cls.partner.id, "group_id": cls.group},
                ),
                cls.env["procurement.group"].Procurement(
                    cls.product_c,
                    10.0,
                    cls.product_c.uom_id,
                    cls.customers,
                    "Test B",
                    "Test B",
                    cls.env.company,
                    {"partner_id": cls.partner.id, "group_id": cls.group},
                ),
            ]
        )
