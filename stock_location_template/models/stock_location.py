# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = "stock.location"

    location_template_id = fields.Many2one(
        comodel_name="stock.location.template",
        string="Location Template"
    )
    auto_generated_from_template = fields.Boolean(
        string="Location generated from template", default=False)

    def _get_location_vals(self, index):
        return {
            "name": self.location_template_id.get_cell_name(index),
            "location_id": self.id,
            "auto_generated_from_template": True,
        }

    def _generate_sublocations(self):
        starting_nbr = self.location_template_id.starting_nbr
        ending_nbr = starting_nbr + self.location_template_id.cells_nbr
        for i in range(starting_nbr, ending_nbr):
            vals = self._get_location_vals(i)
            self.create(vals)

    def _check_can_change_template(self):
        if any(self.child_ids.mapped("auto_generated_from_template")):
            raise ValidationError(
                _("You cannot change the tempalte of a location when there "
                  "are sub-locations that have been generated from this "
                  "template")
            )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if "location_template_id" in vals:
            if res.location_template_id.auto_generate_locations:
                res._generate_sublocations()
        return res

    @api.multi
    def write(self, vals):
        for record in self:
            location_template_id = vals.get("location_template_id", False)
            if location_template_id and record.location_template_id:
                record._check_can_change_template()
            res = super(StockLocation, record).write(vals)
            if location_template_id:
                if record.location_template_id.auto_generate_locations:
                    record._generate_sublocations()
        return res
