# Copyright 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# Copyright 2018-2019 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    corridor = fields.Char('Corridor')
    row = fields.Char('Row')
    rack = fields.Char('Rack')
    level = fields.Char('Level')
    posx = fields.Integer('Box (X)')
    posy = fields.Integer('Box (Y)')
    posz = fields.Integer('Box (Z)')
