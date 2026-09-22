# Copyright 2017-18 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockCycleCountRule(models.Model):
    _name = "stock.cycle.count.rule"
    _description = "Stock Cycle Counts Rules"

    name = fields.Char(required=True)
    rule_type = fields.Selection(
        selection="_selection_rule_types", string="Type of rule", required=True
    )
    rule_description = fields.Char(compute="_compute_rule_description")
    active = fields.Boolean(default=True)
    periodic_qty_per_period = fields.Integer(string="Counts per period", default=1)
    periodic_count_period = fields.Integer(string="Period in days")
    turnover_inventory_value_threshold = fields.Float()
    currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency", compute="_compute_currency_id"
    )
    accuracy_threshold = fields.Float(
        string="Minimum Accuracy Threshold", digits=(3, 2)
    )
    apply_in = fields.Selection(
        string="Apply this rule in:",
        selection=[
            ("warehouse", "Selected warehouses"),
            ("location", "Selected Location Zones."),
        ],
        default="warehouse",
    )
    warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse",
        relation="warehouse_cycle_count_rule_rel",
        column1="rule_id",
        column2="warehouse_id",
        string="Warehouses where applied",
        compute="_compute_warehouse_ids",
        store=True,
        readonly=False,
    )
    location_ids = fields.Many2many(
        comodel_name="stock.location",
        relation="location_cycle_count_rule_rel",
        column1="rule_id",
        column2="location_id",
        string="Zones where applied",
    )

    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = self.env.user.company_id.currency_id

    @api.model
    def _selection_rule_types(self):
        return [
            ("periodic", _("Periodic")),
            ("turnover", _("Value Turnover")),
            ("accuracy", _("Minimum Accuracy")),
            ("zero", _("Zero Confirmation")),
        ]

    @api.constrains("rule_type", "warehouse_ids")
    def _check_zero_rule(self):
        for rec in self:
            if rec.rule_type == "zero" and len(rec.warehouse_ids) > 1:
                raise ValidationError(
                    _(
                        "Zero confirmation rules can only have one warehouse "
                        "assigned."
                    )
                )
            if rec.rule_type == "zero":
                zero_rule = self.search(
                    [
                        ("rule_type", "=", "zero"),
                        ("warehouse_ids", "=", rec.warehouse_ids.id),
                    ]
                )
                if len(zero_rule) > 1:
                    raise ValidationError(
                        _(
                            "You can only have one zero confirmation rule per "
                            "warehouse."
                        )
                    )

    @api.depends("rule_type")
    def _compute_rule_description(self):
        if self.rule_type == "periodic":
            self.rule_description = _(
                "Ensures that at least a defined number "
                "of counts in a given period will "
                "be run."
            )
        elif self.rule_type == "turnover":
            self.rule_description = _(
                "Schedules a count every time the total "
                "turnover of a location exceeds the "
                "threshold. This considers every "
                "product going into/out of the location"
            )
        elif self.rule_type == "accuracy":
            self.rule_description = _(
                "Schedules a count every time the "
                "accuracy of a location goes under a "
                "given threshold."
            )
        elif self.rule_type == "zero":
            self.rule_description = _(
                "Perform an Inventory Adjustment every "
                "time a location in the warehouse runs "
                "out of stock in order to confirm it is "
                "truly empty."
            )
        else:
            self.rule_description = _("(No description provided.)")

    @api.constrains("periodic_qty_per_period", "periodic_count_period")
    def _check_negative_periodic(self):
        for rec in self:
            if rec.periodic_qty_per_period < 1:
                raise ValidationError(
                    _(
                        "You cannot define a negative or null number of counts "
                        "per period."
                    )
                )
            if rec.periodic_count_period < 0:
                raise ValidationError(_("You cannot define a negative period."))

    @api.depends("location_ids")
    def _compute_warehouse_ids(self):
        for record in self:
            wh_ids = []
            for loc in record.location_ids:
                if loc.warehouse_id:  # Make sure warehouse_id is set
                    wh_ids.append(loc.warehouse_id.id)
            wh_ids = list(set(wh_ids))  # Remove duplicates
            record.warehouse_ids = [(6, 0, wh_ids)]

    def compute_rule(self, locs):
        if self.rule_type == "periodic":
            proposed_cycle_counts = self._compute_rule_periodic(locs)
        elif self.rule_type == "turnover":
            proposed_cycle_counts = self._compute_rule_turnover(locs)
        elif self.rule_type == "accuracy":
            proposed_cycle_counts = self._compute_rule_accuracy(locs)
        return proposed_cycle_counts

    @api.model
    def _propose_cycle_count(self, date, location):
        cycle_count = {
            "date": fields.Datetime.from_string(date),
            "location": location,
            "rule_type": self,
            "company_id": location.company_id,
        }
        return cycle_count

    @api.model
    def _compute_rule_periodic(self, locs):
        cycle_counts = []
        for loc in locs:
            latest_inventory_date = (
                self.env["stock.inventory"]
                .search(
                    [
                        ("location_ids", "in", [loc.id]),
                        ("state", "in", ["in_progress", "done", "draft"]),
                    ],
                    order="date desc",
                    limit=1,
                )
                .date
            )
            if latest_inventory_date:
                try:
                    period = self.periodic_count_period / self.periodic_qty_per_period
                    next_date = fields.Datetime.from_string(
                        latest_inventory_date
                    ) + timedelta(days=period)
                    if next_date < datetime.today():
                        next_date = datetime.today()
                except AttributeError as e:
                    raise UserError(
                        _(
                            "Error found determining the frequency of periodic "
                            "cycle count rule. %s"
                        )
                        % str(e)
                    ) from e
            else:
                next_date = datetime.today()
            cycle_count = self._propose_cycle_count(next_date, loc)
            cycle_counts.append(cycle_count)
        return cycle_counts

    @api.model
    def _get_turnover_moves(self, location, date):
        moves = self.env["stock.move"].search(
            [
                "|",
                ("location_id", "=", location.id),
                ("location_dest_id", "=", location.id),
                ("date", ">", date),
                ("state", "=", "done"),
            ]
        )
        return moves

    @api.model
    def _compute_turnover(self, move):
        price = move._get_price_unit()
        turnover = move.product_uom_qty * price
        return turnover

    @api.model
    def _compute_rule_turnover(self, locs):
        cycle_counts = []
        location_ids = locs.mapped("id")
        inventories = self.env["stock.inventory"].search(
            [
                ("location_ids", "in", location_ids),
                ("state", "in", ["confirm", "done", "draft"]),
            ]
        )
        inventory_dates_by_location = {loc.id: [] for loc in locs}
        for inventory in inventories:
            for location in inventory.location_ids:
                if location.id in inventory_dates_by_location:
                    inventory_dates_by_location[location.id].append(inventory.date)

        for loc in locs:
            last_inventories = inventory_dates_by_location.get(loc.id, [])
            if last_inventories:
                latest_inventory = sorted(last_inventories, reverse=True)[0]
                moves = self._get_turnover_moves(loc, latest_inventory)
                if moves:
                    total_turnover = sum(self._compute_turnover(m) for m in moves)
                    try:
                        if total_turnover > self.turnover_inventory_value_threshold:
                            next_date = datetime.today()
                            cycle_count = self._propose_cycle_count(next_date, loc)
                            cycle_counts.append(cycle_count)
                    except AttributeError as e:
                        raise UserError(
                            _(
                                "Error found when comparing turnover "
                                "with the rule threshold. %s"
                            )
                            % str(e)
                        ) from e
            else:
                next_date = datetime.today()
                cycle_count = self._propose_cycle_count(next_date, loc)
                cycle_counts.append(cycle_count)
        return cycle_counts

    def _compute_rule_accuracy(self, locs):
        self.ensure_one()
        cycle_counts = []
        for loc in locs:
            if loc.loc_accuracy < self.accuracy_threshold:
                next_date = datetime.today()
                cycle_count = self._propose_cycle_count(next_date, loc)
                cycle_counts.append(cycle_count)
        return cycle_counts
