# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PushedFlow(models.Model):
    _inherit = "stock.location.path"

    auto_create_group = fields.Boolean(string='Auto-create Procurement Group')

    def _prepare_move_copy_values(self, move_to_copy, new_date):
        """
        Create a procurement group for every picking, not every move.
        We check we don't split pickings by move using the field
        first_backorder_move.
        For the other stock moves we just assign the group created in the
        first move.
        """
        new_move_vals = super(
            PushedFlow, self)._prepare_move_copy_values(
            move_to_copy, new_date)
        if self.auto_create_group and not \
                move_to_copy.picking_id.push_group_id and \
                move_to_copy.first_backorder_move:
            group_data = self._prepare_auto_procurement_group_data()
            group = self.env['procurement.group'].create(group_data)
            new_move_vals['group_id'] = group.id
            move_to_copy.picking_id.push_group_id = group.id
        elif move_to_copy.picking_id.push_group_id:
            new_move_vals['group_id'] = move_to_copy.picking_id.push_group_id.id
        return new_move_vals

    @api.model
    def _prepare_auto_procurement_group_data(self):
        name = self.env['ir.sequence'].next_by_code(
            'procurement.group') or False
        if not name:
            raise UserError(_('No sequence defined for procurement group'))
        return {
            'name': name
        }
