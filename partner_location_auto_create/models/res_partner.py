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
            res['res_id'] = self.location_ids[0].id
            res['view_mode'] = 'form'
        else:
            res['domain'] = [('partner_id', '=', self[0].id)]
            res['view_mode'] = 'tree,form'

        return res

    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)

        if vals.get('is_company', False):
            property_stock_customer = False
            property_stock_supplier = False

            if not vals.get('location_ids', False):
                if partner.customer:
                    property_stock_customer = partner._create_location(
                        'customer')

                if partner.supplier:
                    property_stock_supplier = partner._create_location(
                        'supplier')

            partner.write({
                'property_stock_customer': property_stock_customer,
                'property_stock_supplier': property_stock_supplier,
            })

        return partner

    @api.multi
    def _create_location(self, usage):
        self.ensure_one()
        return self.env['stock.location'].create({
            'name': self.name,
            'usage': usage,
            'partner_id': self.id,
            'company_id': self.company_id.id,
        })

    @api.multi
    def _get_locations(self, usage):
        self.ensure_one()
        return self.location_ids.filtered(lambda l: l.usage == usage)

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)

        if vals.get('customer'):
            for partner in self:
                if partner.is_company:
                    locations = partner._get_locations('customer')

                    if not locations:
                        location = partner._create_location('customer')
                        partner.property_stock_customer = location.id

                    if not partner.property_stock_customer:
                        partner.property_stock_customer = locations[0].id

        if vals.get('supplier'):
            for partner in self:
                if partner.is_company:
                    locations = partner._get_locations('supplier')

                    if not locations:
                        location = partner._create_location('supplier')
                        partner.property_stock_supplier = location.id

                    if not partner.property_stock_supplier:
                        partner.property_stock_supplier = locations[0].id

        return res
