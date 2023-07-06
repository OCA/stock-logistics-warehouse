# Copyright 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2017  Creu Blanca <www.creublanca.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import pycountry

from odoo import api, fields, models


class ResCountry(models.Model):
    _inherit = "res.country"

    code_alpha3 = fields.Char(
        string="Country Code (3-letter)",
        size=3,
        store=True,
        help="ISO 3166-1 alpha-3 (three-letter) code for the country",
        compute="_compute_codes",
    )
    code_numeric = fields.Char(
        string="Country Code (numeric)",
        size=3,
        store=True,
        help="ISO 3166-1 numeric code for the country",
        compute="_compute_codes",
    )

    @api.depends("code")
    def _compute_codes(self):
        for country in self:
            c = False
            for country_type in ["countries", "historic_countries"]:
                try:
                    c = getattr(pycountry, country_type).get(alpha_2=country.code)
                except KeyError:
                    c = getattr(pycountry, country_type).get(alpha2=country.code)
                if c:
                    break
            if c:
                country.code_alpha3 = getattr(c, "alpha_3", getattr(c, "alpha3", False))
                country.code_numeric = c.numeric
            else:
                country.code_alpha3 = False
                country.code_numeric = False
