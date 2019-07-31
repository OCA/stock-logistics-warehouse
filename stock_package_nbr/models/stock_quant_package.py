# Copyright 2017 Sylvain Van Hoof (Okia) <sylvain@okia.be>
# Copyright 2018-2019 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    nbr_packages = fields.Integer('Number of packages', default=1)
