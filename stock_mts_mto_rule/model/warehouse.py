# -*- coding: utf-8 -*-
###############################################################################
#
#    Module for OpenERP
#    Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Florian DA COSTA <florian.dacosta@akretion.com>
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
###############################################################################
from openerp import models, api, fields, exceptions
from openerp.tools.translate import _


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    mto_mts_management = fields.Boolean(
        'Use MTO+MTS rules',
        help='If this new route is selected on product form view, a '
             'purchase order will be created only if the virtual stock is '
             'less than 0 else, the product will be taken from stocks')
    mts_mto_rule_id = fields.Many2one('procurement.rule',
                                      'MTO+MTS rule')

    @api.model
    def _get_mts_mto_rule(self, warehouse):
        route_model = self.env['stock.location.route']
        pull_model = self.env['procurement.rule']
        try:
            mts_mto_route = self.env.ref(
                'stock_mts_mto_rule.route_mto_mts')
        except:
            mts_mto_route = route_model.search([
                ('name', 'like', 'Make To Order + Make To Stock')
            ])
        if not mts_mto_route:
            raise exceptions.Warning(_(
                'Can\'t find any generic MTS+MTO route.'))

        if not warehouse.mto_pull_id:
            raise exceptions.Warning(_(
                'Can\'t find MTO Rule on the warehouse'))

        mts_rules = pull_model.search(
            [('location_src_id', '=', warehouse.lot_stock_id.id),
             ('route_id', '=', warehouse.delivery_route_id.id)])
        if not mts_rules:
            raise exceptions.Warning(_(
                'Can\'t find MTS Rule on the warehouse'))
        return {
            'name': self._format_routename(warehouse, _('MTS+MTO')),
            'route_id': mts_mto_route.id,
            'action': 'split_procurement',
            'mto_rule_id': warehouse.mto_pull_id.id,
            'mts_rule_id': mts_rules[0].id,
            'warehouse_id': warehouse.id,
            'location_id': warehouse.mto_pull_id.location_id.id,
            'picking_type_id': warehouse.mto_pull_id.picking_type_id.id,
        }

    @api.model
    def _get_push_pull_rules(self, warehouse, active, values, new_route_id):
        pull_obj = self.env['procurement.rule']
        res = super(Warehouse, self)._get_push_pull_rules(
            warehouse, active, values, new_route_id)
        customer_location = warehouse._get_partner_locations()
        location_id = customer_location[0].id
        if warehouse.mto_mts_management:
            for pull in res[1]:
                if pull['location_id'] == location_id:
                    pull_mto_mts = pull.copy()
                    pull_mto_mts_id = pull_obj.create(pull_mto_mts)
                    pull.update({
                        'action': 'split_procurement',
                        'mto_rule_id': pull_mto_mts_id.id,
                        'mts_rule_id': pull_mto_mts_id.id,
                        'sequence': 10
                        })
        return res

    @api.multi
    def create_routes(self, warehouse):
        pull_model = self.env['procurement.rule']
        res = super(Warehouse, self).create_routes(warehouse)
        if warehouse.mto_mts_management:
            mts_mto_pull_vals = self._get_mts_mto_rule(warehouse)
            mts_mto_pull = pull_model.create(mts_mto_pull_vals)
            res['mts_mto_rule_id'] = mts_mto_pull.id
        return res

    @api.multi
    def write(self, vals):
        pull_model = self.env['procurement.rule']
        if 'mto_mts_management' in vals:
            if vals.get("mto_mts_management"):
                for warehouse in self:
                    if not warehouse.mts_mto_rule_id:
                        rule_vals = self._get_mts_mto_rule(warehouse)
                        mts_mto_pull = pull_model.create(rule_vals)
                        vals['mts_mto_rule_id'] = mts_mto_pull.id
            else:
                for warehouse in self:
                    if warehouse.mts_mto_rule_id:
                        warehouse.mts_mto_rule_id.unlink()
        res = super(Warehouse, self).write(vals)
        if 'mto_mts_management' in vals:
            self.with_context({'active_test': False}).change_route(
                warehouse, new_delivery_step=warehouse.delivery_steps)
        return res

    @api.model
    def get_all_routes_for_wh(self, warehouse):
        all_routes = super(Warehouse, self).get_all_routes_for_wh(warehouse)
        if (
            warehouse.mto_mts_management and
            warehouse.mts_mto_rule_id.route_id
        ):
            all_routes += [warehouse.mts_mto_rule_id.route_id.id]
        return all_routes

    @api.model
    def _handle_renaming(self, warehouse, name, code):
        res = super(Warehouse, self)._handle_renaming(warehouse, name, code)

        if warehouse.mts_mto_rule_id:
            warehouse.mts_mto_rule_id.name = (
                warehouse.mts_mto_rule_id.name.replace(
                    warehouse.name, name, 1)
            )
        return res

    @api.multi
    def change_route(self, warehouse, new_reception_step=False,
                     new_delivery_step=False):
        res = super(Warehouse, self).change_route(
            warehouse,
            new_reception_step=new_reception_step,
            new_delivery_step=new_delivery_step)

        mts_mto_rule_id = warehouse.mts_mto_rule_id
        if new_delivery_step and mts_mto_rule_id:
            pull_model = self.env['procurement.rule']
            warehouse.mts_mto_rule_id.location_id = (
                warehouse.mto_pull_id.location_id)
            mts_rules = pull_model.search(
                [('location_src_id', '=', warehouse.lot_stock_id.id),
                 ('route_id', '=', warehouse.delivery_route_id.id)])
            warehouse.mts_mto_rule_id.mts_rule_id = mts_rules[0].id
        return res
