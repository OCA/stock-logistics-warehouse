# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    cycle_count_rule_ids = fields.Many2many(
        comodel_name='stock.cycle.count.rule',
        relation='warehouse_cycle_count_rule_rel',
        column1='warehouse_id',
        column2='rule_id',
        string='Cycle Count Rules')
    cycle_count_planning_horizon = fields.Integer(
        string='Cycle Count Planning Horizon (in days)',
        help='Cycle Count planning horizon in days. Only the counts inside '
             'the horizon will be created.')
    counts_for_accuracy_qty = fields.Integer(
        string='Inventories for location accuracy calculation',
        default=1,
        help='Number of latest inventories used to calculate location '
             'accuracy')

    @api.multi
    def get_horizon_date(self):
        self.ensure_one()
        date = datetime.today()
        delta = timedelta(self.cycle_count_planning_horizon)
        date_horizon = date + delta
        return date_horizon

    @api.model
    def _get_cycle_count_locations_search_domain(
            self, parent):
        domain = [('parent_left', '>=', parent.parent_left),
                  ('parent_right', '<=', parent.parent_right),
                  ('cycle_count_disabled', '=', False)]
        return domain

    @api.model
    def _search_cycle_count_locations(self, rule):
        locations = self.env['stock.location']
        if rule.apply_in == 'warehouse':
            locations = self.env['stock.location'].search(
                self._get_cycle_count_locations_search_domain(
                    self.view_location_id))
        elif rule.apply_in == 'location':
            for loc in rule.location_ids:
                locations += self.env['stock.location'].search(
                    self._get_cycle_count_locations_search_domain(loc))
        return locations

    @api.multi
    def _cycle_count_rules_to_compute(self):
        self.ensure_one()
        rules = self.env['stock.cycle.count.rule'].search([
            ('rule_type', '!=', 'zero'), ('warehouse_ids', 'in', self.ids)])
        return rules

    @api.model
    def _prepare_cycle_count(self, cycle_count_proposed):
        return {
            'date_deadline': cycle_count_proposed['date'],
            'location_id': cycle_count_proposed['location'].id,
            'cycle_count_rule_id': cycle_count_proposed[
                'rule_type'].id,
            'state': 'draft'
        }

    @api.multi
    def action_compute_cycle_count_rules(self):
        """ Apply the rule in all the sublocations of a given warehouse(s) and
        returns a list with required dates for the cycle count of each
        location """
        for rec in self:
            proposed_cycle_counts = []
            rules = rec._cycle_count_rules_to_compute()
            for rule in rules:
                locations = rec._search_cycle_count_locations(rule)
                if locations:
                    proposed_cycle_counts.extend(rule.compute_rule(locations))
            if proposed_cycle_counts:
                locations = list(set([d['location'] for d in
                                      proposed_cycle_counts]))
                for loc in locations:
                    proposed_for_loc = list(filter(
                        lambda x: x['location'] == loc, proposed_cycle_counts))
                    earliest_date = min([d['date'] for d in proposed_for_loc])
                    cycle_count_proposed = list(filter(
                        lambda x: x['date'] == earliest_date,
                        proposed_for_loc))[0]
                    domain = [('location_id', '=', loc.id),
                              ('state', 'in', ['draft'])]
                    existing_cycle_counts = self.env[
                        'stock.cycle.count'].search(domain)
                    if existing_cycle_counts:
                        existing_earliest_date = sorted(
                            existing_cycle_counts.mapped('date_deadline'))[0]
                        if (cycle_count_proposed['date'] <
                                existing_earliest_date):
                            cc_to_update = existing_cycle_counts.search([
                                ('date_deadline', '=', existing_earliest_date)
                            ])
                            cc_to_update.write({
                                'date_deadline': cycle_count_proposed['date'],
                                'cycle_count_rule_id': cycle_count_proposed[
                                    'rule_type'].id,
                            })
                    delta = datetime.strptime(
                        cycle_count_proposed['date'],
                        DEFAULT_SERVER_DATETIME_FORMAT) - datetime.today()
                    if not existing_cycle_counts and \
                            delta.days < rec.cycle_count_planning_horizon:
                        cc_vals = self._prepare_cycle_count(
                            cycle_count_proposed)
                        self.env['stock.cycle.count'].create(cc_vals)

    @api.model
    def cron_cycle_count(self):
        _logger.info("stock_cycle_count cron job started.")
        try:
            whs = self.search([])
            whs.action_compute_cycle_count_rules()
        except Exception as e:
            _logger.info(
                "Error while running stock_cycle_count cron job: %s", str(e))
            raise
        _logger.info("stock_cycle_count cron job ended.")
        return True
