#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import api, fields, models


class StockConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _get_consumption_calculation_method(self):
        return [
            ("moves", "Moves (calculate consumption based on Stock Moves)"),
            ("history", "Calculate consumption based on the Product History"),
        ]

    default_consumption_calculation_method = fields.Selection(
        _get_consumption_calculation_method,
        "Consumption Calculation Method",
        default="moves",
        default_model="product.template",
    )
    default_calculation_range = fields.Integer(
        "Calculation Range in days",
        default=365,
        default_model="product.template",
        help="""This field is used if the"""
        """ selected method is based on Stock Moves."""
        """Number of days used for"""
        """ the calculation of the average consumption. For example: if you"""
        """ put 365, the calculation will be done on last year.""",
    )
    default_display_range = fields.Integer(
        "Display Range in days",
        default=1,
        default_model="product.template",
        help="""Examples:
        1 -> Average Consumption per days
        7 -> Average Consumption per week
        30 -> Average Consumption per month""",
    )
    module_product_history = fields.Boolean(
        "View product History", help="This will install product_history module"
    )

    @api.onchange("default_consumption_calculation_method")
    def _onchange_default_consumption_calculation_method(self):
        if self.default_consumption_calculation_method == "history":
            self.module_product_history = True

    @api.onchange("module_product_history")
    def _onchange_module_product_history(self):
        if not self.module_product_history:
            self.default_consumption_calculation_method = "moves"

    def _prepare_values_consumption_to_update_product_tmpl(self, changed_vals):
        values = {}
        if changed_vals.get("default_display_range") is not None:
            values["display_range"] = changed_vals["default_display_range"]
        if changed_vals.get("default_calculation_range") is not None:
            values["calculation_range"] = changed_vals["default_calculation_range"]
        if changed_vals.get("default_consumption_calculation_method") is not None:
            values["consumption_calculation_method"] = changed_vals[
                "default_consumption_calculation_method"
            ]
        return values

    def update_consumption_info_for_products(self, changed_vals):
        values_consumption = self._prepare_values_consumption_to_update_product_tmpl(
            changed_vals
        )
        ProductTemplateSudo = self.env["product.template"].sudo()
        if values_consumption:
            ProductTemplateSudo.search([]).write(values_consumption)

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.update_consumption_info_for_products(
            len(vals_list) > 0 and vals_list[0] or {}
        )
        return res

    def write(self, vals):
        res = super().write(vals)
        self.update_consumption_info_for_products(vals)
        return res
