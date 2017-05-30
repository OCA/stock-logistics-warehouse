# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from datetime import timedelta
from openerp.addons import decimal_precision as dp
from openerp.tools import float_compare, float_round
import operator as py_operator
import logging

_logger = logging.getLogger(__name__)


OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '==': py_operator.eq,
    '!=': py_operator.ne
}


UNIT = dp.get_precision('Product Unit of Measure')


_PRIORITY_LEVEL = [
    ('1_red', 'Red'),
    ('2_yellow', 'Yellow'),
    ('3_green', 'Green')
]


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'
    _description = "Stock Buffer"

    @api.multi
    @api.depends("dlt", "adu", "buffer_profile_id.lead_time_id.factor",
                 "buffer_profile_id.variability_id.factor",
                 "product_uom.rounding")
    def _compute_red_zone(self):
        for rec in self:
            rec.red_base_qty = float_round(
                rec.dlt * rec.adu * rec.buffer_profile_id.lead_time_id.factor,
                precision_rounding=rec.product_uom.rounding)
            rec.red_safety_qty = float_round(
                rec.red_base_qty * rec.buffer_profile_id.variability_id.factor,
                precision_rounding=rec.product_uom.rounding)
            rec.red_zone_qty = rec.red_base_qty + rec.red_safety_qty

    @api.multi
    @api.depends("dlt", "adu", "buffer_profile_id.lead_time_id.factor",
                 "order_cycle", "minimum_order_quantity",
                 "product_uom.rounding")
    def _compute_green_zone(self):
        for rec in self:
            # Using imposed or desired minimum order cycle
            rec.green_zone_oc = float_round(
                rec.order_cycle * rec.adu,
                precision_rounding=rec.product_uom.rounding)
            # Using lead time factor
            rec.green_zone_lt_factor = float_round(
                rec.dlt*rec.adu*rec.buffer_profile_id.lead_time_id.factor,
                precision_rounding=rec.product_uom.rounding)
            # Using minimum order quantity
            rec.green_zone_moq = float_round(
                rec.minimum_order_quantity,
                precision_rounding=rec.product_uom.rounding)

            # The biggest option of the above will be used as the green zone
            #  value
            rec.green_zone_qty = max(rec.green_zone_oc,
                                     rec.green_zone_lt_factor,
                                     rec.green_zone_moq)

            rec.top_of_green = \
                rec.green_zone_qty + rec.yellow_zone_qty + rec.red_zone_qty

    @api.multi
    @api.depends("dlt", "adu", "buffer_profile_id.lead_time_id.factor",
                 "buffer_profile_id.variability_id.factor",
                 "buffer_profile_id.replenish_method",
                 "order_cycle", "minimum_order_quantity",
                 "product_uom.rounding")
    def _compute_yellow_zone(self):
        for rec in self:
            if rec.buffer_profile_id.replenish_method == 'min_max':
                rec.yellow_zone_qty = 0
            else:
                rec.yellow_zone_qty = float_round(
                    rec.dlt * rec.adu,
                    precision_rounding=rec.product_uom.rounding)
            rec.top_of_yellow = rec.yellow_zone_qty + rec.red_zone_qty

    @api.multi
    @api.depends("dlt")
    def _compute_procure_recommended_date(self):
        for rec in self:
            rec.procure_recommended_date = \
                fields.date.today() + timedelta(days=int(rec.dlt))

    @api.multi
    @api.depends("net_flow_position", "dlt", "adu",
                 "buffer_profile_id.lead_time_id.factor",
                 "red_zone_qty", "order_cycle", "minimum_order_quantity",
                 "qty_multiple", "product_uom", "procure_uom_id",
                 "product_uom.rounding",
                 "procurement_ids",
                 "procurement_ids.product_id",
                 "procurement_ids.state", "procurement_ids.product_uom",
                 "procurement_ids.product_qty",
                 "procurement_ids.add_to_net_flow_equation")
    def _compute_procure_recommended_qty(self):
        subtract_qty = self.subtract_procurements_from_orderpoints(self.ids)
        for rec in self:
            procure_recommended_qty = 0.0
            if rec.net_flow_position < rec.top_of_green:
                qty = rec.top_of_green - rec.net_flow_position\
                    - subtract_qty[rec.id]
                if qty >= 0.0:
                    procure_recommended_qty = qty
            else:
                procure_recommended_qty -= subtract_qty[rec.id]
            if procure_recommended_qty > 0.0:
                reste = rec.qty_multiple > 0 and \
                    procure_recommended_qty % rec.qty_multiple or 0.0

                if rec.procure_uom_id:
                    rounding = rec.procure_uom_id.rounding
                else:
                    rounding = rec.product_uom.rounding

                if float_compare(
                        reste, 0.0,
                        precision_rounding=rounding) > 0:
                    procure_recommended_qty += rec.qty_multiple - reste

                if rec.procure_uom_id:
                    product_qty = rec.procure_uom_id._compute_qty(
                        rec.product_id.uom_id.id, procure_recommended_qty,
                        rec.procure_uom_id.id)
                else:
                    product_qty = procure_recommended_qty
            else:
                product_qty = 0.0

            rec.procure_recommended_qty = product_qty

    @api.multi
    @api.depends("red_zone_qty")
    def _compute_order_spike_threshold(self):
        # TODO: Add various methods to compute the spike threshold
        for rec in self:
            rec.order_spike_threshold = 0.5 * rec.red_zone_qty

    buffer_profile_id = fields.Many2one(
        comodel_name='stock.buffer.profile',
        string="Buffer Profile")
    dlt = fields.Float(string="Decoupled Lead Time (days)")
    adu = fields.Float(string="Average Daily Usage (ADU)",
                       default=0.0, digits=UNIT, readonly=True)
    adu_calculation_method = fields.Many2one(
        comodel_name="product.adu.calculation.method",
        string="ADU calculation method")
    adu_fixed = fields.Float(string="Fixed ADU",
                             default=1.0, digits=UNIT)
    order_cycle = fields.Float(string="Minimum Order Cycle (days)")
    minimum_order_quantity = fields.Float(string="Minimum Order Quantity",
                                          digits=UNIT)
    red_base_qty = fields.Float(string="Red Base Qty",
                                compute="_compute_red_zone",
                                digits=UNIT, store=True)
    red_safety_qty = fields.Float(string="Red Safety Qty",
                                  compute="_compute_red_zone",
                                  digits=UNIT, store=True)
    red_zone_qty = fields.Float(string="Red Zone Qty",
                                compute="_compute_red_zone",
                                digits=UNIT, store=True)
    top_of_red = fields.Float(string="Top of Red",
                              related="red_zone_qty", store=True)
    green_zone_qty = fields.Float(string="Green Zone Qty",
                                  compute="_compute_green_zone",
                                  digits=UNIT, store=True)
    green_zone_lt_factor = fields.Float(string="Green Zone Lead Time Factor",
                                        compute="_compute_green_zone",
                                        help="Green zone Lead Time Factor",
                                        store=True)
    green_zone_moq = fields.Float(string="Green Zone Minimum Order Quantity",
                                  compute="_compute_green_zone",
                                  help="Green zone minimum order quantity",
                                  digits=UNIT, store=True)
    green_zone_oc = fields.Float(string="Green Zone Order Cycle",
                                 compute="_compute_green_zone",
                                 help="Green zone order cycle", store=True)
    yellow_zone_qty = fields.Float(string="Yellow Zone Qty",
                                   compute="_compute_yellow_zone",
                                   digits=UNIT, store=True)
    top_of_yellow = fields.Float(string="Top of Yellow",
                                 compute="_compute_yellow_zone",
                                 digits=UNIT, store=True)
    top_of_green = fields.Float(string="Top of Green",
                                compute="_compute_green_zone", digits=UNIT,
                                store=True)
    order_spike_horizon = fields. Float(string="Order Spike Horizon")
    order_spike_threshold = fields.Float(
        string="Order Spike Threshold",
        compute="_compute_order_spike_threshold", digits=UNIT, store=True)
    qualified_demand = fields.Float(string="Qualified demand", digits=UNIT,
                                    readonly=True)
    net_flow_position = fields.Float(string="Net flow position", digits=UNIT,
                                     readonly=True)
    net_flow_position_percent = fields.Float(
        string="Net flow position (% of TOG)", readonly=True)
    planning_priority_level = fields.Selection(
        string="Planning Priority Level", selection=_PRIORITY_LEVEL,
        readonly=True)
    execution_priority_level = fields.Selection(
        string="On-Hand Alert Level",
        selection=_PRIORITY_LEVEL, store=True, readonly=True)
    on_hand_percent = fields.Float(string="On Hand/TOG (%)",
                                   store=True, readonly=True)
    # We override the calculation method for the procure recommended qty
    procure_recommended_qty = fields.Float(
        compute="_compute_procure_recommended_qty", store=True)
    procure_recommended_date = fields.Date(
        compute="_compute_procure_recommended_date")

    _order = 'planning_priority_level asc, net_flow_position asc'

    @api.multi
    @api.onchange("red_zone_qty")
    def onchange_red_zone_qty(self):
        for rec in self:
            rec.product_min_qty = self.red_zone_qty

    @api.multi
    @api.onchange("adu_fixed", "adu_calculation_method")
    def onchange_adu_fixed(self):
        for rec in self:
            if rec.adu_calculation_method.method == 'fixed':
                rec.adu = self.adu_fixed

    @api.multi
    @api.onchange("top_of_green")
    def onchange_green_zone_qty(self):
        for rec in self:
            rec.product_max_qty = self.top_of_green

    @api.model
    def _search_open_stock_moves_domain(self):
        return [('product_id', '=', self.product_id.id),
                ('state', 'in', ['draft', 'waiting', 'confirmed',
                                 'assigned']),
                ('location_dest_id', '=', self.location_id.id)]

    @api.model
    def _stock_move_tree_view(self, lines):
        views = []
        tree_view = self.env.ref('stock.view_move_tree', False)
        if tree_view:
            views += [(tree_view.id, 'tree')]
        form_view = self.env.ref(
            'stock.view_move_form', False)
        if form_view:
            views += [(form_view.id, 'form')]

        return {'type': 'ir.actions.act_window',
                'res_model': 'stock.move',
                'view_type': 'form',
                'views': views,
                'view_mode': 'tree,form',
                'domain': str([('id', 'in', lines.ids)])
                }

    @api.multi
    def open_moves(self):
        self.ensure_one()
        # Utility method used to add an "Open Moves" button in the buffer
        # planning view
        domain = self._search_open_stock_moves_domain()
        records = self.env['stock.move'].search(domain)
        return self._stock_move_tree_view(records)

    @api.model
    def subtract_procurements(self, orderpoint):
        qty = super(StockWarehouseOrderpoint, self).subtract_procurements(
            orderpoint)
        uom_obj = self.env["product.uom"]
        for procurement in orderpoint.procurement_ids:
            if procurement.state not in ('draft', 'cancel') and \
                    procurement.add_to_net_flow_equation:
                qty += uom_obj._compute_qty_obj(
                    procurement.product_uom,
                    procurement.product_qty,
                    procurement.product_id.uom_id)
        if qty >= 0.0:
            return qty
        else:
            return 0.0

    @api.model
    def _past_demand_estimate_domain(self, date_from, date_to, locations):
        return [('location_id', 'in', locations.ids),
                ('product_id', '=', self.product_id.id),
                '|', ('period_id.date_from', '>=', date_from),
                ('period_id.date_to', '<=', date_to)]

    @api.model
    def _past_moves_domain(self, date_from, locations):
        return [('state', '=', 'done'), ('location_id', 'in', locations.ids),
                ('location_dest_id', 'not in', locations.ids),
                ('product_id', '=', self.product_id.id),
                ('date', '>=', date_from)]

    @api.model
    def _compute_adu_past_demand(self):
        horizon = 1
        if not self.adu_calculation_method:
            date_from = fields.Date.today()
        else:
            horizon = self.adu_calculation_method.horizon
            date_from = fields.Date.to_string(
                fields.date.today() - timedelta(days=horizon))
        date_to = fields.Date.today()
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        if self.adu_calculation_method.use_estimates:
            qty = 0.0
            domain = self._past_demand_estimate_domain(date_from, date_to,
                                                       locations)
            for estimate in self.env['stock.demand.estimate'].search(domain):
                qty += estimate.get_quantity_by_date_range(
                    fields.Date.from_string(date_from),
                    fields.Date.from_string(date_to))
            return qty / horizon
        else:
            qty = 0.0
            domain = self._past_moves_domain(date_from, locations)
            for group in self.env['stock.move'].read_group(
                    domain, ['product_id', 'product_qty'], ['product_id']):
                qty += group['product_qty']
            return qty / horizon

    @api.model
    def _future_demand_estimate_domain(self, date_from, date_to, locations):
        return [('location_id', 'in', locations.ids),
                ('product_id', '=', self.product_id.id),
                '|', ('period_id.date_from', '>=', date_from),
                ('period_id.date_to', '<=', date_to)]

    @api.model
    def _future_moves_domain(self, date_to, locations):
        return [('state', 'not in', ['done', 'cancel']),
                ('location_id', 'in', locations.ids),
                ('location_dest_id', 'not in', locations.ids),
                ('product_id', '=', self.product_id.id),
                ('date', '<=', date_to)]

    @api.multi
    def _compute_adu_future_demand(self):
        self.ensure_one()
        horizon = 1
        if not self.adu_calculation_method:
            date_to = fields.Date.today()
        else:
            horizon = self.adu_calculation_method.horizon
            date_to = fields.Date.to_string(
                fields.date.today() + timedelta(days=horizon-1))
        date_from = fields.Date.today()
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        if self.adu_calculation_method.use_estimates:
            qty = 0.0
            domain = self._future_demand_estimate_domain(date_from, date_to,
                                                         locations)
            for estimate in self.env['stock.demand.estimate'].search(domain):
                qty += estimate.get_quantity_by_date_range(
                    fields.Date.from_string(date_from),
                    fields.Date.from_string(date_to))
            return qty / horizon
        else:
            qty = 0.0
            domain = self._future_moves_domain(date_to, locations)
            for group in self.env['stock.move'].read_group(
                    domain, ['product_id', 'product_qty'], ['product_id']):
                qty += group['product_qty']
            return qty / horizon

    @api.multi
    def _calc_adu(self):
        for orderpoint in self:
            if orderpoint.adu_calculation_method.method == 'fixed':
                orderpoint.adu = orderpoint.adu_fixed
            elif orderpoint.adu_calculation_method.method == 'past':
                orderpoint.adu = orderpoint._compute_adu_past_demand()
            elif orderpoint.adu_calculation_method.method == 'future':
                orderpoint.adu = orderpoint._compute_adu_future_demand()
        return True

    @api.multi
    def _search_stock_moves_qualified_demand_domain(self):
        self.ensure_one()
        horizon = self.order_spike_horizon
        if not horizon:
            date_to = fields.Date.to_string(fields.date.today())

        else:
            date_to = fields.Date.to_string(fields.date.today() + timedelta(
                days=horizon))
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        return [('product_id', '=', self.product_id.id),
                ('state', 'in', ['draft', 'waiting', 'confirmed',
                                 'assigned']),
                ('location_id', 'in', locations.ids),
                ('location_dest_id', 'not in', locations.ids),
                ('date', '<=', date_to)]

    @api.multi
    def _calc_qualified_demand(self):
        for rec in self:
            rec.refresh()
            rec.qualified_demand = 0.0
            domain = rec._search_stock_moves_qualified_demand_domain()
            moves = self.env['stock.move'].search(domain)
            demand_by_days = {}
            move_dates = [fields.Datetime.from_string(dt).date() for dt in
                          moves.mapped('date')]
            for move_date in move_dates:
                demand_by_days[move_date] = 0.0
            for move in moves:
                date = fields.Datetime.from_string(move.date).date()
                demand_by_days[date] += move.product_qty
            for date in demand_by_days.keys():
                if demand_by_days[date] >= rec.order_spike_threshold \
                        or date == fields.date.today():
                    rec.qualified_demand += demand_by_days[date]
        return True

    @api.multi
    def _calc_net_flow_position(self):
        for rec in self:
            rec.refresh()
            rec.net_flow_position = rec.product_location_qty + \
                rec.incoming_location_qty - rec.qualified_demand
            usage = 0.0
            if rec.top_of_green:
                usage = round((rec.net_flow_position /
                              rec.top_of_green*100), 2)
            rec.net_flow_position_percent = usage
            for procurement in rec.procurement_ids:
                if procurement.state not in ('draft', 'cancel'):
                    procurement.add_to_net_flow_equation = False
        return True

    @api.multi
    def _calc_planning_priority(self):
        for rec in self:
            rec.refresh()
            if rec.net_flow_position >= rec.top_of_yellow:
                rec.planning_priority_level = '3_green'
            elif rec.net_flow_position >= rec.top_of_red:
                rec.planning_priority_level = '2_yellow'
            else:
                rec.planning_priority_level = '1_red'

    @api.multi
    def _calc_execution_priority(self):
        for rec in self:
            rec.refresh()
            if rec.product_location_qty_available_not_res >= rec.top_of_red:
                rec.execution_priority_level = '3_green'
            elif rec.product_location_qty_available_not_res >= \
                    rec.top_of_red*0.5:
                rec.execution_priority_level = '2_yellow'
            else:
                rec.execution_priority_level = '1_red'
            if rec.top_of_green:
                rec.on_hand_percent = round((
                    (rec.product_location_qty_available_not_res /
                     rec.top_of_green)*100), 2)
            else:
                rec.on_hand_percent = 0.0

    @api.model
    def cron_ddmrp(self, automatic=False):
        """calculate key DDMRP parameters for each orderpoint
        Called by cronjob.
        """
        _logger.info("Start cron_ddmrp.")
        orderpoints = self.search([])
        for op in orderpoints:
            try:
                op._calc_adu()
                op._calc_qualified_demand()
                op._calc_net_flow_position()
                op._calc_planning_priority()
                op._calc_execution_priority()
                if automatic:
                    self.env.cr.commit()
            except Exception:
                if automatic:
                    self.env.cr.rollback()
                    _logger.exception(
                        'Fail to create recurring invoice for orderpoint %s',
                        op.name)
                else:
                    raise
        _logger.info("End cron_ddmrp.")

        return True
