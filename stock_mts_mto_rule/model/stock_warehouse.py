# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, exceptions
from odoo.tools.translate import _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    mto_mts_management = fields.Boolean(
        'Use MTO+MTS rules',
        help='If this new route is selected on product form view, a '
             'purchase order will be created only if the virtual stock is '
             'less than 0 else, the product will be taken from stocks')
    mts_mto_rule_id = fields.Many2one('procurement.rule',
                                      'MTO+MTS rule')

    @api.multi
    def _get_mts_mto_rule(self):
        self.ensure_one()
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

        if not self.mto_pull_id:
            raise exceptions.Warning(_(
                'Can\'t find MTO Rule on the warehouse'))

        mts_rules = pull_model.search(
            [('location_src_id', '=', self.lot_stock_id.id),
             ('route_id', '=', self.delivery_route_id.id)])
        if not mts_rules:
            raise exceptions.Warning(_(
                'Can\'t find MTS Rule on the warehouse'))
        return {
            'name': self._format_routename(route_type='mts_mto'),
            'route_id': mts_mto_route.id,
            'action': 'split_procurement',
            'mto_rule_id': self.mto_pull_id.id,
            'mts_rule_id': mts_rules[0].id,
            'warehouse_id': self.id,
            'location_id': self.mto_pull_id.location_id.id,
            'picking_type_id': self.mto_pull_id.picking_type_id.id,
        }

    def _get_mto_pull_rules_values(self, route_values):
        """
        Prevent changing standard MTO rules' action from "move"
        """
        pull_rules_list = super(StockWarehouse, self).\
            _get_mto_pull_rules_values(route_values)
        for pull_rule in pull_rules_list:
            pull_rule['action'] = 'move'

        return pull_rules_list

    @api.multi
    def create_routes(self):
        pull_model = self.env['procurement.rule']
        res = super(StockWarehouse, self).create_routes()
        if self.mto_mts_management:
            mts_mto_pull_vals = self._get_mts_mto_rule()
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
                        rule_vals = warehouse._get_mts_mto_rule()
                        mts_mto_pull = pull_model.create(rule_vals)
                        vals['mts_mto_rule_id'] = mts_mto_pull.id
            else:
                for warehouse in self:
                    if warehouse.mts_mto_rule_id:
                        warehouse.mts_mto_rule_id.unlink()
        res = super(StockWarehouse, self).write(vals)
        if 'mto_mts_management' in vals:
            self.with_context({'active_test': False})._update_routes()
        return res

    @api.model
    def get_all_routes_for_wh(self):
        all_routes = super(StockWarehouse, self).get_all_routes_for_wh()

        if self.mto_mts_management and self.mts_mto_rule_id.route_id:
            all_routes += self.mts_mto_rule_id.route_id

        return all_routes

    @api.multi
    def _update_name_and_code(self, name, code):
        res = super(StockWarehouse, self)._update_name_and_code(name, code)
        if not name:
            return res
        for warehouse in self.filtered('mts_mto_rule_id'):
            warehouse.mts_mto_rule_id.name = (
                warehouse.mts_mto_rule_id.name.replace(
                    warehouse.name, name, 1,
                )
            )
        return res

    def _get_route_name(self, route_type):
        names = {'mts_mto': _('MTS+MTO')}
        if route_type in names:
            return names[route_type]

        return super(StockWarehouse, self)._get_route_name(route_type)

    @api.multi
    def _update_routes(self):
        res = super(StockWarehouse, self)._update_routes()
        for warehouse in self:
            mts_mto_rule_id = warehouse.mts_mto_rule_id
            if warehouse.delivery_steps and mts_mto_rule_id:
                pull_model = self.env['procurement.rule']
                warehouse.mts_mto_rule_id.location_id = \
                    warehouse.mto_pull_id.location_id
                mts_rules = pull_model.search([
                    ('location_src_id', '=', warehouse.lot_stock_id.id),
                    ('location_id', '=', warehouse.mto_pull_id.location_id.id),
                    ('route_id', '=', warehouse.delivery_route_id.id),
                ])
                warehouse.mts_mto_rule_id.mts_rule_id = mts_rules[0].id
        return res
