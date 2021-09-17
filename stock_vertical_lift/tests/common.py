# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.stock_location_tray.tests import common


class VerticalLiftCase(common.LocationTrayTypeCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.shuttle = cls.env.ref(
            "stock_vertical_lift.stock_vertical_lift_demo_shuttle_1"
        )
        cls.product_socks = cls.env.ref("stock_vertical_lift.product_running_socks")
        cls.product_recovery = cls.env.ref("stock_vertical_lift.product_recovery_socks")
        cls.vertical_lift_loc = cls.env.ref(
            "stock_vertical_lift.stock_location_vertical_lift"
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.location_1a = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_1a"
        )
        cls.location_1a_x1y1 = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_1a_x1y1"
        )
        cls.location_1a_x2y1 = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_1a_x2y1"
        )
        cls.location_1a_x3y1 = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_1a_x3y1"
        )
        cls.location_1a_x1y2 = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_1a_x1y2"
        )
        cls.location_1b = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_1b"
        )
        cls.location_1b_x1y1 = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_1b_x1y1"
        )
        cls.location_1b_x1y2 = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_1b_x1y2"
        )
        cls.location_2a = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_2a"
        )
        cls.location_2a_x1y1 = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_2a_x1y1"
        )

    @classmethod
    def _update_qty_in_location(
        cls, location, product, quantity, package=None, lot=None
    ):
        quants = cls.env["stock.quant"]._gather(
            product, location, lot_id=lot, package_id=package, strict=True
        )
        # this method adds the quantity to the current quantity, so remove it
        quantity -= sum(quants.mapped("quantity"))
        cls.env["stock.quant"]._update_available_quantity(
            product, location, quantity, package_id=package, lot_id=lot
        )

    def _open_screen(self, mode, shuttle=None):
        getattr(shuttle or self.shuttle, "switch_{}".format(mode))()
        # opening the screen can do some initialization for the steps
        action = (shuttle or self.shuttle).action_open_screen()
        return self.env[action["res_model"]].browse(action["res_id"])

    @classmethod
    def _create_simple_picking_out(cls, product, quantity):
        stock_loc = cls.env.ref("stock.stock_location_stock")
        customer_loc = cls.env.ref("stock.stock_location_customers")
        picking_type = cls.env.ref("stock.picking_type_out")
        partner = cls.env.ref("base.res_partner_1")
        return cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": partner.id,
                "location_id": stock_loc.id,
                "location_dest_id": customer_loc.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": quantity,
                            "picking_type_id": picking_type.id,
                            "location_id": stock_loc.id,
                            "location_dest_id": customer_loc.id,
                        },
                    )
                ],
            }
        )

    @classmethod
    def _create_simple_picking_in(cls, product, quantity, dest_location):
        supplier_loc = cls.env.ref("stock.stock_location_suppliers")
        picking_type = cls.env.ref("stock.picking_type_in")
        partner = cls.env.ref("base.res_partner_1")
        return cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": partner.id,
                "location_id": supplier_loc.id,
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
                            "picking_type_id": picking_type.id,
                            "location_id": supplier_loc.id,
                            "location_dest_id": dest_location.id,
                        },
                    )
                ],
            }
        )

    @classmethod
    def _create_inventory(cls, products):
        """Create a draft inventory

        Products is a list of tuples (bin location, product).
        """
        values = {
            "name": "Test Inventory",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "product_uom_id": product.uom_id.id,
                        "location_id": location.id,
                    },
                )
                for location, product in products
            ],
        }
        inventory = cls.env["stock.inventory"].create(values)
        inventory.action_start()
        return inventory

    def _test_button_release(self, move_lines, expected_state):
        # for the test, we'll consider all the lines has been delivered
        for move_line in move_lines:
            move_line.qty_done = move_line.product_qty
        move_lines.picking_id._action_done()
        # release, no further operation in queue
        operation = self.shuttle._operation_for_mode()
        # the release button can be used only in the state... release
        operation.state = "release"
        result = operation.button_release()
        self.assertEqual(operation.state, expected_state)
        self.assertFalse(operation.current_move_line_id)
        expected_result = {
            "effect": {
                "fadeout": "slow",
                "message": _("Congrats, you cleared the queue!"),
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }
        self.assertEqual(result, expected_result)
