#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import api, fields, models

HISTORY_RANGE = [
    # TODO: find a way to speed up the day history computation before
    # enabling this in selection again
    # ('days', 'Days'),
    ("weeks", "Week"),
    ("months", "Month"),
]

DAYS_IN_RANGE = {
    "days": 1,
    "weeks": 7,
    "months": 30,
}


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_consumption_calculation_method(self):
        selection = super()._get_consumption_calculation_method()
        selection.append(
            (
                "history",
                "History (calculate consumption based on the Product\
            History)",
            ),
        )
        return selection

    # Columns section
    consumption_calculation_method = fields.Selection(
        _get_consumption_calculation_method, default="moves"
    )
    history_range = fields.Selection(HISTORY_RANGE, default="weeks")
    product_history_ids = fields.One2many(
        comodel_name="product.history",
        inverse_name="product_tmpl_id",
        string="History",
        compute="_compute_product_history_ids",
    )
    number_of_periods = fields.Integer(
        "Number of History periods",
        default=6,
        help="""Number of valid history periods used for the calculation""",
    )

    # Private section
    @api.depends("history_range")
    def _compute_product_history_ids(self):
        for template in self:
            histories = self.env["product.history"].search(
                [
                    ("product_tmpl_id", "in", template.ids),
                    ("history_range", "=", template.history_range),
                ]
            )
            template.product_history_ids = histories

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.nb_days",
        "product_variant_ids.total_consumption",
        "consumption_calculation_method",
        "calculation_range",
    )
    def _compute_average_consumption(self):
        res = super()._compute_average_consumption()
        for template in self:
            if template.consumption_calculation_method == "history":
                template._average_consumption_history()
        return res

    def _average_consumption_history(self):
        self.ensure_one()
        average_consumption = 0.0
        total_consumption = 0.0
        if self.product_variant_ids:
            number_of_periods = max(
                product.number_of_periods_real for product in self.product_variant_ids
            )
            total_consumption = sum(
                product.total_consumption for product in self.product_variant_ids
            )
            average_consumption = (
                number_of_periods
                and (
                    total_consumption
                    / number_of_periods
                    / DAYS_IN_RANGE[self.history_range]
                )
                or 0.0
            )
            self.average_consumption = average_consumption
            self.total_consumption = total_consumption
