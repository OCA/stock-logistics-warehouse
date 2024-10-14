# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import namedtuple

from odoo.tests.common import SavepointCase

ShortMoveInfo = namedtuple(
    "ShortMoveInfo", ["product", "location_dest", "qty", "package_id"]
)


class TestLocationPackageRestrictionCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """
        Data:
            2 products: product_1, product_2
            2 packages: pack_1, pack_2
            1 new warehouse: warehouse1
            2 new locations: location1 and location2 are children of
                             warehouse1's stock location and without
                             restriction
            stock:
                * 50 product_1 in location_1
                * 0 product_2 in stock
        """
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        Product = cls.env["product.product"]
        cls.product_1 = Product.create(
            {"name": "Wood", "type": "product", "uom_id": cls.uom_unit.id}
        )
        cls.product_2 = Product.create(
            {"name": "Stone", "type": "product", "uom_id": cls.uom_unit.id}
        )

        # Warehouses
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
                "code": "BWH",
            }
        )

        # Locations
        cls.location_1 = cls.env["stock.location"].create(
            {
                "name": "TestLocation1",
                "posx": 3,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )

        cls.location_2 = cls.env["stock.location"].create(
            {
                "name": "TestLocation2",
                "posx": 4,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )

        # Packages:
        Package = cls.env["stock.quant.package"]
        cls.pack_1 = Package.create({"name": "Package 1"})
        cls.pack_2 = Package.create({"name": "Package 2"})

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

        # partner
        cls.partner_1 = cls.env["res.partner"].create(
            {"name": "Raumschmiede.de", "email": "info@raumschmiede.de"}
        )

        # picking type
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")

        cls.StockMove = cls.env["stock.move"]
        cls.StockPicking = cls.env["stock.picking"]

    @classmethod
    def _change_product_qty(cls, product, location, package, qty):
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "package_id": package and package.id,
                "inventory_quantity": qty,
                "location_id": location.id,
            }
        )

    @classmethod
    def _get_package_in_location(cls, location):
        return (
            cls.env["stock.quant"]
            .search([("location_id", "=", location.id)])
            .mapped("package_id")
        )

    @classmethod
    def _create_and_assign_picking(cls, short_move_infos, location_dest=None):
        location_dest = location_dest or cls.location_1
        picking_in = cls.StockPicking.create(
            {
                "partner_id": cls.partner_1.id,
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": location_dest.id,
            }
        )
        for move_info in short_move_infos:
            cls.StockMove.create(
                {
                    "name": move_info.product.name,
                    "product_id": move_info.product.id,
                    "product_uom_qty": move_info.qty,
                    "product_uom": move_info.product.uom_id.id,
                    "picking_id": picking_in.id,
                    "location_id": cls.supplier_location.id,
                    "location_dest_id": move_info.location_dest.id,
                }
            )

        picking_in.action_confirm()
        for move_info in short_move_infos:
            line = picking_in.move_line_ids.filtered(
                lambda x: x.product_id.id == move_info.product.id
            )
            if line:
                line.result_package_id = move_info.package_id
        return picking_in

    @classmethod
    def _process_picking(cls, picking):
        picking.action_assign()
        for line in picking.move_line_ids:
            line.qty_done = line.product_qty
        picking.button_validate()
