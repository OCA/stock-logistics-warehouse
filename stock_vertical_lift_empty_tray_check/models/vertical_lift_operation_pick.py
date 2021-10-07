# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.tools import float_is_zero


class VerticalLiftOperationPick(models.Model):
    _inherit = "vertical.lift.operation.pick"

    def button_release(self):
        """Release the operation, go to the next

        By default it asks the user to inspect visually if the tray is empty.
        """
        icp = self.env["ir.config_parameter"].sudo()
        tray_check = icp.get_param("vertical_lift_empty_tray_check")
        skip_zero_quantity_check = self.env.context.get("skip_zero_quantity_check")
        if not skip_zero_quantity_check and tray_check:
            uom_rounding = self.product_id.uom_id.rounding
            if float_is_zero(self.tray_qty, precision_rounding=uom_rounding):
                return self._check_zero_quantity()

        return super().button_release()

    def _check_zero_quantity(self):
        """Show the wizard to check for real-zero quantity."""
        view = self.env.ref(
            "stock_vertical_lift_empty_tray_check."
            "vertical_lift_operation_pick_zero_check_view_form"
        )
        wizard_model = "vertical.lift.operation.pick.zero.check"
        wizard = self.env[wizard_model].create(
            {"vertical_lift_operation_pick_id": self.id}
        )
        return {
            "name": _("Is the tray empty?"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "target": "new",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "res_model": wizard_model,
            "res_id": wizard.id,
            "context": self.env.context,
        }
