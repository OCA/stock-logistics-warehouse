from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    vertical_lift_empty_tray_check = fields.Boolean(
        "Vertical lift: Check Empty Tray",
        default=False,
        config_parameter="vertical_lift_empty_tray_check",
    )
