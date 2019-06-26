# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.addons.base_sparse_field.models.fields import Serialized


class VerticalLiftTrayType(models.Model):
    _name = 'vertical.lift.tray.type'
    _description = 'Vertical Lift Tray Type'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    rows = fields.Integer(required=True)
    cols = fields.Integer(required=True)
    active = fields.Boolean(default=True)
    tray_matrix = Serialized(compute='_compute_tray_matrix')
    location_ids = fields.One2many(
        comodel_name='stock.location',
        inverse_name='vertical_lift_tray_type_id',
    )
    # TODO do we want box size, or a many2one to 'product.packaging'?
    # TODO add the code in the name_search

    @api.depends('rows', 'cols')
    def _compute_tray_matrix(self):
        for record in self:
            # As we only want to show the disposition of
            # the tray, we generate a "full" tray, we'll
            # see all the boxes on the web widget.
            # (0 means empty, 1 means used)
            cells = self._generate_cells_matrix(default_state=1)
            record.tray_matrix = {'selected': [], 'cells': cells}

    def _generate_cells_matrix(self, default_state=0):
        return [[default_state] * self.cols for __ in range(self.rows)]

    @api.constrains('active')
    def _vertical_lift_check_active(self):
        for record in self:
            if record.active:
                continue
            if record.location_ids:
                location_bullets = [
                    ' - {}'.format(location.display_name)
                    for location in record.location_ids
                ]
                raise exceptions.ValidationError(
                    _(
                        "The tray type {} is used by the following locations "
                        "and cannot be archived:\n\n{}"
                    ).format(record.name, '\n'.join(location_bullets))
                )

    @api.constrains('rows', 'cols')
    def _vertical_lift_check_rows_cols(self):
        for record in self:
            if record.location_ids:
                location_bullets = [
                    ' - {}'.format(location.display_name)
                    for location in record.location_ids
                ]
                raise exceptions.ValidationError(
                    _(
                        "The tray type {} is used by the following locations, "
                        "it's size cannot be changed:\n\n{}"
                    ).format(record.name, '\n'.join(location_bullets))
                )

    @api.multi
    def open_locations(self):
        action = self.env.ref('stock.action_location_form').read()[0]
        action['domain'] = [('vertical_lift_tray_type_id', 'in', self.ids)]
        if len(self.ids) == 1:
            action['context'] = {'default_vertical_lift_tray_type_id': self.id}
        return action
