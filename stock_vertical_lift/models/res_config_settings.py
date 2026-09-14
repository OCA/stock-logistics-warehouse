# stock-logistics-warehouse/18.0/stock_vertical_lift/models/res_config_settings.py

from odoo import fields, models


class StockVerticalLiftSettings(models.TransientModel):
    _inherit = "res.config.settings"

    vertical_lift_secret = fields.Char(
        string="Secret for Vertical Lift API",
        config_parameter="stock_vertical_lift.secret",
    )
    vertical_lift_pick_by_priority = fields.Boolean(
        related="company_id.vertical_lift_pick_by_priority",
        readonly=False,
    )
    vertical_lift_pick_skipped_last = fields.Boolean(
        related="company_id.vertical_lift_pick_skipped_last",
        readonly=False,
    )
