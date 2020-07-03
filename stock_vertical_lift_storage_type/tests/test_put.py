# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock_vertical_lift.tests.common import VerticalLiftCase


class TestPut(VerticalLiftCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.wh_input_stock_loc_id.active = True
        cls.wh.int_type_id.active = True

        # used on the vertical lift top level
        LocStorageType = cls.env["stock.location.storage.type"]
        cls.location_storage_type_buffer = LocStorageType.create(
            {"name": "VLift Buffer"}
        )
        cls.location_storage_type_small_8x = LocStorageType.create(
            {"name": "Small 8x", "only_empty": True}
        )

        PackageStorageType = cls.env["stock.package.storage.type"]
        # package storage type used only to putaway a package temporarily in
        # the vertical lift view location before being put in a shuttle, which
        # will not be configured in any shuttle's locations, we'll use when
        # the operator knows that a good has to go in a shuttle, but doesn't
        # know yet in which tray type: when the first putaway is done, the good
        # stays in the vertical lift view (above the shuttles), then, when the
        # user scans the package in a shuttle, they have to scan a tray type.
        cls.package_storage_type_buffer = PackageStorageType.create(
            {
                "name": "VLift Box",
                "location_storage_type_ids": [
                    (4, cls.location_storage_type_buffer.id),
                ],
            }
        )
        # storage type used for Tray 1A, user won't have to scan a tray type
        # when this storage type is already set on the package
        cls.package_storage_type_small_8x = PackageStorageType.create(
            {
                "name": "Small 8x",
                "location_storage_type_ids": [
                    (4, cls.location_storage_type_small_8x.id),
                    (4, cls.location_storage_type_buffer.id),
                ],
            }
        )

        cls.location_shuttle1 = cls.shuttle.location_id
        cls.vertical_lift_loc.location_storage_type_ids = (
            cls.location_storage_type_buffer
        )
        cls.vertical_lift_loc.pack_putaway_strategy = "none"
        cls.location_shuttle1.location_storage_type_ids = (
            cls.location_storage_type_small_8x
        )
        cls.location_shuttle1.pack_putaway_strategy = "ordered_locations"

        cls.env["stock.storage.location.sequence"].create(
            {
                "package_storage_type_id": cls.package_storage_type_small_8x.id,
                "sequence": 1,
                "location_id": cls.vertical_lift_loc.id,
            }
        )
        cls.env["stock.storage.location.sequence"].create(
            {
                "package_storage_type_id": cls.package_storage_type_small_8x.id,
                "sequence": 2,
                "location_id": cls.location_shuttle1.id,
            }
        )

        cls.package = cls.env["stock.quant.package"].create({})
        cls._update_qty_in_location(
            cls.wh.wh_input_stock_loc_id, cls.product_socks, 10, package=cls.package
        )

        cls.int_picking = cls._create_simple_picking_int(
            cls.product_socks, 10, cls.vertical_lift_loc
        )
        cls.int_picking.action_confirm()
        cls.int_picking.action_assign()

    @classmethod
    def _create_simple_picking_int(cls, product, quantity, dest_location):
        return cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.wh.int_type_id.id,
                "location_id": cls.wh.wh_input_stock_loc_id.id,
                "location_dest_id": dest_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": quantity,
                            "picking_type_id": cls.wh.int_type_id.id,
                            "location_id": cls.wh.wh_input_stock_loc_id.id,
                            "location_dest_id": dest_location.id,
                        },
                    )
                ],
            }
        )

    def test_storage_type_put_away(self):
        self.package.package_storage_type_id = self.package_storage_type_small_8x
        move_line = self.int_picking.move_line_ids
        self.assertEqual(move_line.location_dest_id, self.vertical_lift_loc)
        self.assertEqual(
            move_line.package_level_id.location_dest_id, self.vertical_lift_loc
        )

        operation = self._open_screen("put")
        # we begin with an empty screen, user has to scan a package, product,
        # or lot
        self.assertEqual(operation.state, "scan_source")
        operation.on_barcode_scanned(self.package.name)

        self.assertEqual(operation.current_move_line_id, move_line)
        # the dest location was Vertical Lift, it has been change to Vertical
        # Lift/Shuttle 1, and the computation from there took the first cell
        # available, we should be the pos x1 and y1 in the tray A.
        self.assertEqual(move_line.location_dest_id, self.location_1a_x1y1)
        self.assertEqual(
            move_line.package_level_id.location_dest_id, self.location_1a_x1y1
        )

        # the state goes straight to "save", as we don't need to scan the tray type
        # when a putaway is available
        self.assertEqual(operation.state, "save")

    def test_storage_type_not_configured(self):
        # if we do have a storage type, but the storage type is not used in the
        # shuttle (although it may be used on the lift view location, so we can have an
        # initial putaway rule that puts the package in the lift view location first),
        # we have to ask to scan a tray type
        self.package.package_storage_type_id = self.package_storage_type_buffer
        move_line = self.int_picking.move_line_ids
        self.assertEqual(move_line.location_dest_id, self.vertical_lift_loc)
        self.assertEqual(
            move_line.package_level_id.location_dest_id, self.vertical_lift_loc
        )

        operation = self._open_screen("put")
        # we begin with an empty screen, user has to scan a package, product,
        # or lot
        self.assertEqual(operation.state, "scan_source")
        operation.on_barcode_scanned(self.package.name)

        self.assertEqual(operation.current_move_line_id, move_line)
        # it stays here, as the put-away has no rule to put the "buffer box" in
        # any location
        self.assertEqual(move_line.location_dest_id, self.vertical_lift_loc)

        # and the user has to scan a tray type (so we are back to the normal
        # flow, tested in stock_vertical_lift)
        self.assertEqual(operation.state, "scan_tray_type")
