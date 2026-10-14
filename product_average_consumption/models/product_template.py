#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_consumption_calculation_method(self):
        return [
            ("moves", "Moves (calculate consumption based on Stock Moves)"),
        ]

    # Columns Section
    average_consumption = fields.Float(compute="_compute_average_consumption")
    displayed_average_consumption = fields.Float(
        compute="_compute_displayed_average_consumption",
        string="Average Consumption (Range)",
    )
    total_consumption = fields.Float(compute="_compute_average_consumption")
    nb_days = fields.Integer(
        compute="_compute_average_consumption",
        string="Real Calculation Range (days)",
        help="""The calculation will be done for the last 365 days or"""
        """ since the first stock move of the product if it's"""
        """ more recent""",
    )
    consumption_calculation_method = fields.Selection(
        _get_consumption_calculation_method,
        string="Calculation Method",
        default="moves",
    )
    display_range = fields.Integer(
        "Display Range in days",
        default=1,
        help=(
            "Examples:\n"
            "1 -> Average Consumption per days\n"
            "7 -> Average Consumption per week\n"
            "30 -> Average Consumption per month\n"
        ),
    )
    calculation_range = fields.Integer(
        "Asked Calculation Range (days)",
        default=365,
        help=(
            "Number of days used for the calculation of the average "
            "consumption. For example: if you put 365, the calculation will "
            "be done on last year."
        ),
    )

    def _load_average_consumption_fields(self):
        return ["average_consumption", "total_consumption", "nb_days"]

    # Fields Function Section
    @api.depends(
        "product_variant_ids",
        "product_variant_ids.nb_days",
        "product_variant_ids.total_consumption",
        "consumption_calculation_method",
        "calculation_range",
    )
    def _compute_average_consumption(self):
        for template in self:
            template.average_consumption = 0.0
            template.total_consumption = 0.0
            template.nb_days = 0
            if template.consumption_calculation_method == "moves":
                template._average_consumption_moves()

    def _average_consumption_moves(self):
        self.ensure_one()
        nb_days = 0
        total_consumption = 0.0
        average_consumption = 0.0
        if self.product_variant_ids:
            nb_days = max(self.product_variant_ids.mapped("nb_days"))
            total_consumption = sum(
                self.product_variant_ids.mapped("total_consumption")
            )
            average_consumption = nb_days and (total_consumption / nb_days) or 0.0
        self.nb_days = nb_days
        self.total_consumption = total_consumption
        self.average_consumption = average_consumption

    @api.depends("display_range", "average_consumption")
    def _compute_displayed_average_consumption(self):
        for template in self:
            template.displayed_average_consumption = (
                template.average_consumption * template.display_range
            )
