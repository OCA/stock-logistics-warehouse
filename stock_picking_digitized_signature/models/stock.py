# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        index=True,
        default=lambda self: self.env.user,
    )
    customer_signature = fields.Binary(
        string='Customer acceptance',
    )

    @api.multi
    def action_picking_send(self):
        self.ensure_one()
        template = self.env.ref(
            'stock_picking_digitized_signature.email_picking_template',
            False,
        )
        compose_form = self.env.ref('mail.email_compose_message_wizard_form',
                                    False)
        ctx = dict(
            default_model='stock.picking',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def create(self, values):
        picking = super(StockPicking, self).create(values)
        if picking.customer_signature:
            values = {'customer_signature': picking.customer_signature}
            picking._track_signature(values, 'customer_signature')
        return picking

    @api.multi
    def write(self, values):
        self._track_signature(values, 'customer_signature')
        return super(StockPicking, self).write(values)
