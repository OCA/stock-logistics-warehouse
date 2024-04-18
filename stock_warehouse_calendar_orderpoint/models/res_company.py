# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    orderpoint_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Reordering Calendar",
        help="Calendar used to compute the lead date of reordering rules\n"
        "This value will be used as default value for new warehouses linked to this"
        " company",
    )
    orderpoint_on_workday_policy = fields.Selection(
        [
            ("skip_to_first_workday", "Skip to first workday"),
            ("skip_all_non_workdays", "Skip non-workdays"),
        ],
        string="Reordering on Workday Policy",
        help="Policy to postpone the lead date to the first available workday:\n"
        "* skip to first workday: compute the date using lead delay days as solar"
        " days, then skip to the next workday if the result is not a workday"
        " (eg: run action on Friday with 2 days lead delay -> the result is Sunday ->"
        " skip to the first following workday, Monday)\n"
        "* skip non-workdays: compute the order date consuming lead delay days only on"
        " (eg: run action on Friday with 2 days lead delay -> skip Saturday and Sunday"
        " -> start consuming lead days on Monday as first lead day -> the result is"
        " Tuesday)\n"
        "This value will be used as default value for new warehouses linked to this"
        " company",
        default="skip_to_first_workday",  # Retro-compatible default value
    )
