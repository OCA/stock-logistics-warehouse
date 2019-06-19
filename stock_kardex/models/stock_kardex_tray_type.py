# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockKardexTrayType(models.Model):
    _name = 'stock.kardex.tray.type'
    _description = 'Stock Kardex Tray Type'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    rows = fields.Integer(required=True)
    cols = fields.Integer(required=True)
    active = fields.Boolean(default=True)
    tray_matrix = fields.Serialized(compute='_compute_tray_matrix')
    # TODO do we want box size, or a many2one to 'product.packaging'?

    @api.depends('rows', 'cols')
    def _compute_tray_matrix(self):
        for record in self:
            # As we only want to show the disposition of
            # the tray, we generate a "full" tray, we'll
            # see all the boxes on the web widget.
            # (0 means empty, 1 means used)
            cells = self._generate_cells_matrix(default_state=1)
            record.tray_matrix = {'selected': None, 'cells': cells}

    def _generate_cells_matrix(self, default_state=0):
        return [[default_state] * self.cols for __ in range(self.rows)]

    # TODO prevent to set active=False on a type used in a location
    # TODO we should not be able to change cells and rows for types used
    # in locations
