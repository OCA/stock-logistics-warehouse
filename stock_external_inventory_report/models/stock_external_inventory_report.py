# Copyright 2026 Camptocamp SA
# @author Hadrien Huvelle <hadrien.huvelle@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

# Kinds of activities scheduled by the comparison, see `_get_activity_types()`
ACTIVITY_DISCREPANCY = "discrepancy"
ACTIVITY_ZERO_COST = "zero_cost"
ACTIVITY_MISSING_PRODUCT = "missing_product"


class StockExternalInventoryReport(models.Model):
    _name = "stock.external.inventory.report"
    _description = "External Inventory Report"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True
    _order = "create_date desc, id desc"

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: (
            self.env["ir.sequence"].next_by_code("stock.external.inventory.report")
            or self.env._("New")
        ),
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        required=True,
        readonly=True,
        index=True,
        check_company=True,
        help="The external stock is compared with the stock of this warehouse.",
    )
    external_reference = fields.Char(
        help="Reference of the report in the external system."
    )
    report_date = fields.Datetime(default=fields.Datetime.now, required=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", store=True
    )
    discrepancy_user_id = fields.Many2one(
        "res.users",
        string="Discrepancy Responsible",
        compute="_compute_discrepancy_user_id",
        store=True,
        readonly=False,
        precompute=True,
        check_company=True,
        tracking=True,
        help="Gets the activities of the report. Defaults to the external "
        "inventory responsible of the warehouse; without one, no activity is "
        "scheduled.",
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("processed", "Processed"),
            ("obsolete", "Obsolete"),
        ],
        default="new",
        required=True,
        copy=False,
        tracking=True,
    )
    line_ids = fields.One2many(
        "stock.external.inventory.report.line", "report_id", string="Lines", copy=True
    )
    line_count = fields.Integer(compute="_compute_line_counters")
    reviewed_line_count = fields.Integer(compute="_compute_line_counters")
    total_variance_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_totals", store=True
    )
    over_threshold_line_count = fields.Integer(compute="_compute_totals", store=True)
    zero_cost_line_count = fields.Integer(compute="_compute_totals", store=True)
    comparison_has_error = fields.Boolean(
        copy=False,
        help="Set when the last comparison failed. The report is stuck with "
        "unresolved lines until this is fixed and retried.",
    )
    comparison_error_message = fields.Text(copy=False)
    comparison_date = fields.Datetime(
        readonly=True,
        copy=False,
        help="When the lines were last compared with the stock successfully.",
    )

    @api.private
    def process_comparisons_and_alerts(self):
        """Compare the reports with the warehouse stock and schedule the alerts.

        Run right away; ``stock_external_inventory_report_queue`` runs it in
        jobs.
        """
        return self._process_comparisons_and_alerts()

    def action_process_comparisons(self):
        """Button: compare the reports with the warehouse stock."""
        self.process_comparisons_and_alerts()
        return True

    def _process_comparisons_and_alerts(self):
        """Compare the lines with the warehouse stock and schedule the alerts.

        A failure is flagged on the report, also when the transaction is rolled
        back (e.g. by a job runner), then raised again.
        """
        for report in self:
            try:
                report.line_ids._resolve_external_values(report.warehouse_id)
                report._schedule_discrepancy_activities()
            except Exception as exc:
                # A job runner (e.g. queue_job's) rolls the transaction back
                # when the job fails: write the flag on a separate cursor so
                # it survives.
                report._write_comparison_error(str(exc))
                raise
            else:
                report.write(
                    {
                        "comparison_date": fields.Datetime.now(),
                        "comparison_has_error": False,
                        "comparison_error_message": False,
                    }
                )
        return True

    def _write_comparison_error(self, message):
        """Flag the comparison error ``message`` on a separate cursor."""
        self.ensure_one()
        with self.env.registry.cursor() as new_cr:
            new_env = api.Environment(new_cr, self.env.uid, self.env.context)
            new_env[self._name].browse(self.id).write(
                {
                    "comparison_has_error": True,
                    "comparison_error_message": message,
                }
            )

    @api.model
    def _get_discrepancy_threshold(self):
        """Return the variance amount above which a line is a discrepancy."""
        return 100.0

    @api.depends("warehouse_id")
    def _compute_discrepancy_user_id(self):
        for report in self:
            report.discrepancy_user_id = report.warehouse_id.external_inventory_user_id

    @api.depends("line_ids.line_state")
    def _compute_line_counters(self):
        for report in self:
            report.line_count = len(report.line_ids)
            report.reviewed_line_count = len(
                report.line_ids.filtered(lambda line: line.line_state != "new")
            )

    @api.depends(
        "line_ids.variance_amount",
        "line_ids.over_threshold",
        "line_ids.zero_standard_price",
    )
    def _compute_totals(self):
        for report in self:
            report.total_variance_amount = sum(
                report.line_ids.mapped("variance_amount")
            )
            report.over_threshold_line_count = len(
                report.line_ids.filtered("over_threshold")
            )
            report.zero_cost_line_count = len(
                report.line_ids.filtered("zero_standard_price")
            )

    @api.model_create_multi
    def create(self, vals_list):
        reports = super().create(vals_list)
        # A newly received report obsoletes any still-pending previous one for
        # the same warehouse.
        # TODO Check if a report may be partially obsoleted?
        self.search(
            [
                ("state", "=", "new"),
                ("warehouse_id", "in", reports.warehouse_id.ids),
                ("id", "not in", reports.ids),
            ]
        ).action_set_obsolete()
        reports._schedule_discrepancy_activities()
        return reports

    def write(self, vals):
        blocked_fields = set(vals) - {
            "state",
            "message_follower_ids",
            "activity_ids",
            "comparison_has_error",
            "comparison_error_message",
            "comparison_date",
        }
        if blocked_fields and self.filtered(lambda rec: rec.state == "obsolete"):
            raise UserError(
                self.env._(
                    "Obsolete inventory reports cannot be modified. "
                    "Create a new report instead."
                )
            )
        result = super().write(vals)
        if "state" in vals:
            self.filtered(lambda rec: rec.state != "new")._cancel_open_activities()
        if any(
            field_name in vals for field_name in ("line_ids", "discrepancy_user_id")
        ):
            self._schedule_discrepancy_activities()
        return result

    def action_set_obsolete(self):
        self.filtered(lambda rec: rec.state != "obsolete").write({"state": "obsolete"})
        return True

    def action_mark_processed(self):
        if self.line_ids.filtered(lambda line: line.line_state == "new"):
            raise UserError(
                self.env._(
                    "All lines must be reviewed before marking the report as processed."
                )
            )
        self.write({"state": "processed"})
        return True

    def action_apply_stock_overwrite(self):
        for report in self:
            if report.state == "obsolete":
                raise UserError(
                    self.env._(
                        "Obsolete inventory reports cannot apply stock overwrite."
                    )
                )
            target_lines = report.line_ids.filtered(
                lambda line: (
                    line.line_state == "new"
                    and line.product_id
                    and line.location_id
                    and not float_is_zero(
                        line.delta_qty,
                        precision_rounding=line.product_uom_id.rounding or 0.01,
                    )
                )
            )
            target_lines.action_apply_stock_overwrite()
            report._sync_state_with_lines()
        return True

    def _sync_state_with_lines(self):
        self.filtered(
            lambda rec: rec.state == "new"
            and rec.line_ids
            and not rec.line_ids.filtered(lambda line: line.line_state == "new")
        ).write({"state": "processed"})

    @api.model
    def _get_activity_types(self):
        """Return the activity type of each kind of activity of the comparison.

        Override it to use other types.

        :return: dict ``{kind: mail.activity.type}``
        """
        return {
            ACTIVITY_DISCREPANCY: self.env.ref(
                "stock_external_inventory_report.mail_activity_type_discrepancy"
            ),
            ACTIVITY_ZERO_COST: self.env.ref(
                "stock_external_inventory_report.mail_activity_type_zero_cost"
            ),
            ACTIVITY_MISSING_PRODUCT: self.env.ref(
                "stock_external_inventory_report.mail_activity_type_missing_product"
            ),
        }

    def _cancel_open_activities(self):
        if not self:
            return
        activity_types = self.env["mail.activity.type"].union(
            *self._get_activity_types().values()
        )
        self.env["mail.activity"].search(
            [
                ("res_model", "=", self._name),
                ("res_id", "in", self.ids),
                ("activity_type_id", "in", activity_types.ids),
            ]
        ).unlink()

    def _schedule_discrepancy_activities(self):
        reports = self.filtered(lambda rec: rec.state == "new")
        reports._cancel_open_activities()
        activity_types = self._get_activity_types()
        for report in reports:
            if not report.discrepancy_user_id:
                continue

            over_threshold_lines = report.line_ids.filtered(
                lambda line: (
                    line.line_state == "new"
                    and line.product_id
                    and line.location_id
                    and line.over_threshold
                )
            )
            if over_threshold_lines:
                report.activity_schedule(
                    activity_type_id=activity_types[ACTIVITY_DISCREPANCY].id,
                    summary=activity_types[ACTIVITY_DISCREPANCY].name,
                    note=report._build_discrepancy_note(over_threshold_lines),
                    user_id=report.discrepancy_user_id.id,
                )

            zero_cost_lines = report.line_ids.filtered(
                lambda line: (
                    line.line_state == "new"
                    and line.product_id
                    and line.location_id
                    and line.zero_standard_price
                )
            )
            if zero_cost_lines:
                report.activity_schedule(
                    activity_type_id=activity_types[ACTIVITY_ZERO_COST].id,
                    summary=activity_types[ACTIVITY_ZERO_COST].name,
                    note=report._build_zero_cost_note(zero_cost_lines),
                    user_id=report.discrepancy_user_id.id,
                )

            missing_product_lines = report.line_ids.filtered(
                lambda line: line.line_state == "new" and line.product_not_found
            )
            if missing_product_lines:
                report.activity_schedule(
                    activity_type_id=activity_types[ACTIVITY_MISSING_PRODUCT].id,
                    summary=activity_types[ACTIVITY_MISSING_PRODUCT].name,
                    note=report._build_missing_product_note(missing_product_lines),
                    user_id=report.discrepancy_user_id.id,
                )

    def _build_discrepancy_note(self, lines):
        self.ensure_one()
        bullets = Markup("".join(self._discrepancy_line_bullet(line) for line in lines))
        return Markup("<p>%s</p><ul>%s</ul>") % (
            self.env._(
                "The following inventory lines exceed the %(threshold).2f "
                "%(currency)s discrepancy threshold:",
                threshold=self._get_discrepancy_threshold(),
                currency=self.currency_id.name,
            ),
            bullets,
        )

    def _build_zero_cost_note(self, lines):
        self.ensure_one()
        bullets = Markup("".join(self._zero_cost_line_bullet(line) for line in lines))
        return Markup("<p>%s</p><ul>%s</ul>") % (
            self.env._(
                "The following products have a standard cost equal to 0. "
                "Please review the product cost first:",
            ),
            bullets,
        )

    def _discrepancy_line_bullet(self, line):
        return "<li>{}</li>".format(
            self.env._(
                "%(product)s @ %(location)s%(lot)s: Delta %(delta).2f, "
                "Variance %(variance).2f %(currency)s",
                product=line.product_id.display_name,
                location=line.location_id.display_name,
                lot=(
                    self.env._(" (Lot: %(lot)s)", lot=line.lot_id.name)
                    if line.lot_id
                    else ""
                ),
                delta=line.delta_qty,
                variance=line.variance_amount,
                currency=line.currency_id.name,
            )
        )

    def _zero_cost_line_bullet(self, line):
        return "<li>{}</li>".format(
            self.env._(
                "%(product)s @ %(location)s%(lot)s: external %(external).2f / "
                "Odoo %(odoo).2f",
                product=line.product_id.display_name,
                location=line.location_id.display_name,
                lot=(
                    self.env._(" (Lot: %(lot)s)", lot=line.lot_id.name)
                    if line.lot_id
                    else ""
                ),
                external=line.external_qty,
                odoo=line.odoo_qty,
            )
        )

    def _build_missing_product_note(self, lines):
        self.ensure_one()
        bullets = Markup(
            "".join(self._missing_product_line_bullet(line) for line in lines)
        )
        return Markup("<p>%s</p><ul>%s</ul>") % (
            self.env._(
                "The following external product codes could not be matched with an "
                "Odoo product:",
            ),
            bullets,
        )

    def _missing_product_line_bullet(self, line):
        return "<li>{}</li>".format(
            self.env._(
                "Code %(code)s (qty %(qty).2f, stock_type %(stock_type)s)",
                code=line.external_product_code or self.env._("(empty)"),
                qty=line.external_qty,
                stock_type=line.stock_type or self.env._("(empty)"),
            )
        )
