# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import HttpCase, tagged


@tagged("-standard", "tour", "post_install", "-at_install")
class TestSaveAndReleaseTour(HttpCase):
    def setUp(self):
        super().setUp()
        self.env["ir.config_parameter"].sudo().set_param(
            "vertical_lift_empty_tray_check", True
        )
        shuttle = self.env.ref("stock_vertical_lift.stock_vertical_lift_demo_shuttle_1")
        picking = self.env.ref(
            "stock_vertical_lift.stock_picking_out_demo_vertical_lift_1"
        )
        shuttle.switch_pick()
        action = shuttle.action_open_screen()
        operation = self.env[action["res_model"]].browse(action["res_id"])
        # Same state as on the customer's screen: "Pick goods and save",
        # on a line that empties its tray cell.
        operation.current_move_line_id = picking.move_line_ids[0]
        operation.state = "save"
        window_action = self.env["ir.actions.act_window"].create(
            {
                "name": "Pick screen",
                "res_model": operation._name,
                "view_mode": "form",
                "view_id": self.env.ref(
                    "stock_vertical_lift.vertical_lift_operation_pick_screen_view"
                ).id,
            }
        )
        self.url = f"/odoo/action-{window_action.id}/{operation.id}"

    def test_popup_kept_on_refresh(self):
        self.start_tour(
            self.url, "vertical_lift_empty_tray_check_popup_refresh", login="admin"
        )
