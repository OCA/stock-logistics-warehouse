# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import UserError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import timedelta, datetime


class StockCycleCountRule(models.Model):
    _name = 'stock.cycle.count.rule'
    _description = "Stock Cycle Counts Rules"

    @api.one
    def _compute_currency(self):
        self.currency_id = self.env.user.company_id.currency_id

    @api.model
    def _selection_rule_types(self):
        return [
            ('periodic', _('Periodic')),
            ('turnover', _('Value Turnover')),
            ('accuracy', _('Minimum Accuracy')),
            ('zero', _('Zero Confirmation'))]

    @api.one
    @api.constrains('rule_type', 'warehouse_ids')
    def _check_zero_rule(self):
        if self.rule_type == 'zero' and len(self.warehouse_ids) > 1:
            raise UserError(
                _('Zero confirmation rules can only have one warehouse '
                  'assigned.')
            )
        if self.rule_type == 'zero':
            zero_rule = self.search([
                ('rule_type', '=', 'zero'),
                ('warehouse_ids', '=', self.warehouse_ids.id)])
            if len(zero_rule) > 1:
                raise UserError(
                    _('You can only have one zero confirmation rule per '
                      'warehouse.')
                )

    @api.onchange('rule_type')
    def _get_rule_description(self):
        if self.rule_type == 'periodic':
            self.rule_description = _('Ensures that at least a defined number '
                                      'of counts in a given period will '
                                      'be run.')
        elif self.rule_type == 'turnover':
            self.rule_description = _('Schedules a count every time the total '
                                      'turnover of a location exceeds the '
                                      'threshold. This considers every '
                                      'product going into/out of the location')
        elif self.rule_type == 'accuracy':
            self.rule_description = _('Schedules a count every time the '
                                      'accuracy of a location goes under a '
                                      'given threshold.')
        elif self.rule_type == 'zero':
            self.rule_description = _('Perform an Inventory Adjustment every '
                                      'time a location in the warehouse runs '
                                      'out of stock in order to confirm it is '
                                      'truly empty.')
        else:
            self.rule_description = _('(No description provided.)')

    @api.constrains('periodic_qty_per_period', 'periodic_count_period')
    def _check_negative_periodic(self):
        if self.periodic_qty_per_period < 1:
            raise UserError(
                _('You cannot define a negative or null number of counts per '
                  'period.')
            )
        if self.periodic_count_period < 0:
            raise UserError(
                _('You cannot define a negative period.')
            )

    @api.onchange('location_ids')
    def _get_warehouses(self):
        """Get the warehouses for the selected locations."""
        wh_ids = []
        for loc in self.location_ids:
            wh_ids.append(loc.get_warehouse(loc))
        wh_ids = list(set(wh_ids))
        self.warehouse_ids = self.env['stock.warehouse'].browse(wh_ids)

    name = fields.Char('Name', required=True)
    rule_type = fields.Selection(selection="_selection_rule_types",
                                 string='Type of rule',
                                 required=True)
    rule_description = fields.Char(string='Rule Description',
                                   compute=_get_rule_description)
    active = fields.Boolean(string='Active', default=True)
    periodic_qty_per_period = fields.Integer(string='Counts per period',
                                             default=1)
    periodic_count_period = fields.Integer(string='Period in days')
    turnover_inventory_value_threshold = fields.Float(
        string='Turnover Inventory Value Threshold')
    currency_id = fields.Many2one(comodel_name='res.currency',
                                  string='Currency',
                                  compute=_compute_currency)
    accuracy_threshold = fields.Float(string='Minimum Accuracy Threshold',
                                      digits=(3, 2))
    apply_in = fields.Selection(
        string='Apply this rule in:',
        selection=[('warehouse', 'Selected warehouses'),
                   ('location', 'Selected Location Zones.')],
        default='warehouse')
    warehouse_ids = fields.Many2many(
        comodel_name='stock.warehouse',
        relation='warehouse_cycle_count_rule_rel', column1='rule_id',
        column2='warehouse_id', string='Warehouses where applied')
    location_ids = fields.Many2many(
        comodel_name='stock.location',
        relation='location_cycle_count_rule_rel', column1='rule_id',
        column2='location_id', string='Zones where applied')

    def compute_rule(self, locs):
        if self.rule_type == 'periodic':
            proposed_cycle_counts = self._compute_rule_periodic(locs)
        elif self.rule_type == 'turnover':
            proposed_cycle_counts = self._compute_rule_turnover(locs)
        elif self.rule_type == 'accuracy':
            proposed_cycle_counts = self._compute_rule_accuracy(locs)
        return proposed_cycle_counts

    @api.model
    def _propose_cycle_count(self, date, location):
        cycle_count = {
            'date': date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'location': location,
            'rule_type': self
        }
        return cycle_count

    @api.model
    def _compute_rule_periodic(self, locs):
        cycle_counts = []
        for loc in locs:
            last_inventories = self.env['stock.inventory'].search([
                ('location_id', '=', loc.id),
                ('state', 'in', ['confirm', 'done', 'draft'])]).mapped('date')
            if last_inventories:
                latest_inventory = sorted(last_inventories, reverse=True)[0]
                try:
                    period = self.periodic_count_period / \
                        self.periodic_qty_per_period
                    next_date = datetime.strptime(
                        latest_inventory,
                        DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                        days=period)
                    if next_date < datetime.today():
                        next_date = datetime.today()
                except Exception as e:
                    raise UserError(
                        _('Error found determining the frequency of periodic '
                          'cycle count rule. %s') % e.message)
            else:
                next_date = datetime.today()
            cycle_count = self._propose_cycle_count(next_date, loc)
            cycle_counts.append(cycle_count)
        return cycle_counts

    @api.model
    def _get_turnover_moves(self, location, date):
        moves = self.env['stock.move'].search([
            '|', ('location_id', '=', location.id),
            ('location_dest_id', '=', location.id),
            ('date', '>', date),
            ('state', '=', 'done')])
        return moves

    @api.model
    def _compute_turnover(self, move):
        price = move.get_price_unit(move)
        turnover = move.product_uom_qty * price
        return turnover

    @api.model
    def _compute_rule_turnover(self, locs):
        cycle_counts = []
        for loc in locs:
            last_inventories = self.env['stock.inventory'].search([
                ('location_id', '=', loc.id),
                ('state', 'in', ['confirm', 'done', 'draft'])]).mapped('date')
            if last_inventories:
                latest_inventory = sorted(last_inventories, reverse=True)[0]
                moves = self._get_turnover_moves(loc, latest_inventory)
                if moves:
                    total_turnover = 0.0
                    for m in moves:
                        turnover = self._compute_turnover(m)
                        total_turnover += turnover
                    try:
                        if total_turnover > \
                                self.turnover_inventory_value_threshold:
                            next_date = datetime.today()
                            cycle_count = self._propose_cycle_count(next_date,
                                                                    loc)
                            cycle_counts.append(cycle_count)
                    except Exception as e:
                        raise UserError(_(
                            'Error found when comparing turnover with the '
                            'rule threshold. %s') % e.message)
            else:
                next_date = datetime.today()
                cycle_count = self._propose_cycle_count(next_date, loc)
                cycle_counts.append(cycle_count)
        return cycle_counts

    @api.model
    def _compute_rule_accuracy(self, locs):
        cycle_counts = []
        for loc in locs:
            if loc.loc_accuracy < self.accuracy_threshold:
                next_date = datetime.today()
                cycle_count = self._propose_cycle_count(next_date, loc)
                cycle_counts.append(cycle_count)
        return cycle_counts
