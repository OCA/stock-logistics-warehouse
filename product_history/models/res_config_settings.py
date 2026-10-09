#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import fields, models


class ProductHistorySettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_history_range = fields.Selection(
        [
            ("days", "Days"),
            ("weeks", "Week"),
            ("months", "Month"),
        ],
        "Product History Display Range",
        default="weeks",
        default_model="product.product",
    )

    default_number_of_periods = fields.Integer(
        "Number of valid history periods used for the calculation",
        default=6,
        default_model="product.template",
        help="""This field is used if the selected method is based on"""
        """ Product History""",
    )

    def _prepare_values_consumption_to_update_product_tmpl(self, changed_vals):
        values = super()._prepare_values_consumption_to_update_product_tmpl(
            changed_vals
        )
        if changed_vals.get("default_number_of_periods") is not None:
            values["number_of_periods"] = changed_vals["default_number_of_periods"]
        if changed_vals.get("default_history_range") is not None:
            values["history_range"] = changed_vals["default_history_range"]
        return values
