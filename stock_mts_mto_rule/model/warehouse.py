# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, exceptions
from odoo.tools.translate import _


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
            'name': warehouse._format_routename(route_type='mts_mto'),
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
            self.with_context({'active_test': False})._update_routes()
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

    def _get_route_name(self, route_type):
        names = {'mts_mto': _('MTS+MTO')}
        if route_type in names:
            return names[route_type]

        return super(Warehouse, self)._get_route_name(route_type)

    @api.multi
    def _update_routes(self):
        res = super(Warehouse, self)._update_routes()

        mts_mto_rule_id = self.mts_mto_rule_id
        if self.delivery_steps and mts_mto_rule_id:
            pull_model = self.env['procurement.rule']
            self.mts_mto_rule_id.location_id = self.mto_pull_id.location_id
            mts_rules = pull_model.search([
                ('location_src_id', '=', self.lot_stock_id.id),
                ('route_id', '=', self.delivery_route_id.id),
            ])
            self.mts_mto_rule_id.mts_rule_id = mts_rules[0].id
        return res
