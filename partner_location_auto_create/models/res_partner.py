# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('location_ids')
    def count_locations(self):
        self.locations_count = len(self.location_ids)

    locations_count = fields.Integer(compute='count_locations', store=False)

    location_ids = fields.One2many(
        'stock.location', 'partner_id', string='Locations')

    @api.multi
    def button_locations(self):
        self.ensure_one()

        res = {
            'name': _('Locations'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.location',
            'view_type': 'form',
        }

        if len(self.location_ids) == 1:
            res['res_id'] = self.location_ids.id
            res['view_mode'] = 'form'
        else:
            res['domain'] = [('partner_id', '=', self.id)]
            res['view_mode'] = 'tree,form'

        return res

    @api.one
    def _create_main_partner_location(self):
        if self.customer and self.property_stock_customer.partner_id != self:
            location_customer = (
                self.get_main_location('customer') or
                self._create_main_location('customer'))

            self.write({'property_stock_customer': location_customer})

        if self.supplier and self.property_stock_supplier.partner_id != self:
            location_supplier = (
                self.get_main_location('supplier') or
                self._create_main_location('supplier'))

            self.write({'property_stock_supplier': location_supplier})

    @api.model
    def create(self, vals):
        """ The first time a partner is created, a main customer
        and / or supplier location is created for this partner """
        partner = super(ResPartner, self).create(vals)

        if vals.get('is_company', False):
            partner._create_main_partner_location()

        return partner

    @api.multi
    def _create_main_location(self, usage):
        self.ensure_one()

        parent = (
            self.get_main_location(usage) or
            self.company_id.get_default_location(usage)
        )

        return self.env['stock.location'].create({
            'name': self.name,
            'usage': usage,
            'partner_id': self.id,
            'company_id': self.company_id.id,
            'location_id': parent.id,
            'main_partner_location': True,
        })

    @api.multi
    def get_main_location(self, usage):
        self.ensure_one()
        return self.location_ids.filtered(
            lambda l: l.usage == usage and l.main_partner_location)

    @api.multi
    def write(self, vals):
        if vals.get('name'):
            for partner in self:
                locations = partner.location_ids.filtered(
                    lambda l: l.name == partner.name)
                locations.write({'name': vals.get('name')})

        res = super(ResPartner, self).write(vals)

        if vals.get('is_company'):
            self._create_main_partner_location()

        for partner in self:
            if (
                (vals.get('customer') or vals.get('supplier')) and
                partner.is_company
            ):
                partner._create_main_partner_location()

        if 'active' in vals:
            self.location_ids.write({'active': vals['active']})

        return res
