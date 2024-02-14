from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_show_transit_location_stock_wizard = fields.Boolean(
        "Display also transit location lines in sale line stock popup.",
        implied_group="sale_stock_on_hand_popup.group_show_transit_location_stock_wizard",
        default=False,
    )
