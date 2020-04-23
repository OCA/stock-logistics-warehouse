# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockLocationTemplate(models.Model):
    _name = "stock.location.template"
    _description = "Stock Location Type"

    active = fields.Boolean(default=True)
    name = fields.Char(string="Name")
    location_ids = fields.One2many(
        comodel_name='stock.location',
        inverse_name='location_template_id',
        string='Stock Location',
        copy=False,
    )
    location_count = fields.Integer(
        '# Locations', compute='_compute_location_count',
        help="The number of locations that share the location template")
    cells_nbr = fields.Integer(string="Number of Cells", default=0)
    digits = fields.Integer(string="Digits to use in nomenclature", default=2)
    starting_nbr = fields.Integer(string="Starting number", default=1)
    cells_nomenclature = fields.Char(
        string="Cells Nomenclature",
        help="Use the character %c that will be replaced by the "
             "corresponding cell number"
    )
    cell_name_example = fields.Char(
        string="Cell Naming example", compute="_compute_cell_name_example")
    auto_generate_locations = fields.Boolean(
        string="Auto Generate Stock Locations")
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        required=False,
        string='Company'
    )

    @api.multi
    def _compute_location_count(self):
        for record in self:
            record.location_count = len(record.location_ids)

    def get_cell_name(self, nbr):
        name = ""
        if self.cells_nomenclature and self.digits:
            name = self.cells_nomenclature.replace(
                "%c", str(nbr).zfill(self.digits))
        return name

    @api.depends("digits", "cells_nomenclature")
    def _compute_cell_name_example(self):
        self.ensure_one()
        self.cell_name_example = self.get_cell_name(1)
