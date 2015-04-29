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
        'Use MTO+MTS rules')
    mts_mto_rule_id = fields.Many2one('procurement.rule',
                                      'MTO+MTS rule')

    @api.model
    def _get_mts_mto_mto_rule(self, warehouse):
        return {
            'name': self._format_routename(warehouse, _('MTS+MTO : MTO')),
            'route_id': False,
        }

    @api.model
    def _get_mts_mto_mts_rule(self, warehouse):
        return {
            'name': self._format_routename(warehouse, _('MTS+MTO : MTS')),
            'route_id': False,
            'procure_method': 'make_to_stock',
        }

    @api.model
    def _get_mts_mto_rule(self, warehouse):
        route_model = self.env['stock.location.route']
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

        return {
            'name': self._format_routename(warehouse, _('MTS+MTO')),
            'route_id': mts_mto_route.id,
            'action': 'split_procurement',
        }

    @api.model
    def create_mts_mto_rules(self, warehouse):
        model_rule = warehouse.mto_pull_id
        mts_pull_vals = self._get_mts_mto_mts_rule(warehouse)
        mts_pull = model_rule.copy(mts_pull_vals)
        mto_pull_vals = self._get_mts_mto_mto_rule(warehouse)
        mto_pull_vals['mts_pull_rule_id'] = mts_pull.id
        mto_pull = model_rule.copy(mto_pull_vals)

        mts_mto_pull_vals = self._get_mts_mto_rule(warehouse)
        mts_mto_pull_vals.update({'mts_rule_id': mts_pull.id,
                                  'mto_rule_id': mto_pull.id})
        mts_mto_pull = model_rule.copy(mts_mto_pull_vals)

        res = {
            'mts_rule_id': mts_pull.id,
            'mto_rule_id': mto_pull.id,
            'mts_mto_rule_id': mts_mto_pull.id,
        }
        return res

    @api.multi
    def create_routes(self, warehouse):
        res = super(Warehouse, self).create_routes(warehouse)
        if warehouse.mto_mts_management:
            vals = self.create_mts_mto_rules(warehouse)
            res['mts_mto_rule_id'] = vals.get('mts_mto_rule_id', False)
        return res

    @api.multi
    def write(self, vals):
        if 'mto_mts_management' in vals:
            if vals.get("mto_mts_management"):
                for warehouse in self:
                    if not warehouse.mts_mto_rule_id:
                        rule_vals = self.create_mts_mto_rules(warehouse)
                        vals['mts_mto_rule_id'] = rule_vals.get(
                            'mts_mto_rule_id', False)
            else:
                for warehouse in self:
                    if warehouse.mts_mto_rule_id:
                        warehouse.mts_mto_rule_id.mts_rule_id.unlink()
                        warehouse.mts_mto_rule_id.mto_rule_id.unlink()
                        warehouse.mts_mto_rule_id.unlink()
        return super(Warehouse, self).write(vals)

    @api.model
    def get_all_routes_for_wh(self, warehouse):
        all_routes = super(Warehouse, self).get_all_routes_for_wh(warehouse)
        if (
            warehouse.mto_mts_management and
            warehouse.mts_mto_mto_rule_id.route_id
        ):
            all_routes += [warehouse.mts_mto_rule_id.route_id.id]
        return all_routes

    @api.model
    def _handle_renaming(self, warehouse, name, code):
        res = super(Warehouse, self)._handle_renaming(warehouse, name, code)

        if warehouse.mts_mto_rule_id:
            warehouse.mts_mto_rule_id.mts_rule_id.name = (
                warehouse.mts_mto_rule_id.mts_rule_id.name.replace(
                    warehouse.name, name, 1)
            )
            warehouse.mts_mto_rule_id.mto_rule_id.name = (
                warehouse.mts_mto_rule_id.mto_rule_id.name.replace(
                    warehouse.name, name, 1)
            )
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
            model_rule = warehouse.mto_pull_id
            rule_ids = [
                mts_mto_rule_id.id,
                mts_mto_rule_id.mts_rule_id.id,
                mts_mto_rule_id.mto_rule_id.id
            ]
            pull_model = self.env['procurement.rule']
            vals = {
                'location_id': model_rule.location_id.id,
                'location_src_id': model_rule.location_src_id.id,
            }
            pull_model.write(rule_ids, vals)
        return res
