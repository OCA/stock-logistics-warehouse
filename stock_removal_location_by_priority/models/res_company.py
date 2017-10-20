# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    removal_priority_active = fields.Boolean(
        string="Use 'Removal Priority' in Locations",
        help="Adds an extra field in Locations named 'Removal Priority'."
             "When removing stock from Locations, this priority will apply"
             "whenever the incoming dates of the same stock in several "
             "locations are the same.")
