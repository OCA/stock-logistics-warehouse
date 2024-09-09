# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResCompany(models.Model):

    _name = "res.company"
    _inherit = ["res.company", "stock.exclude.location.mixin"]
