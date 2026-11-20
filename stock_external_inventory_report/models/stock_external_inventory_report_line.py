# Copyright 2026 Camptocamp SA
# @author Hadrien Huvelle <hadrien.huvelle@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

from odoo.addons.stock_warehouse_stock_type.models.stock_warehouse import (
    STOCK_TYPE_FREE,
)


class StockExternalInventoryReportLine(models.Model):
    _name = "stock.external.inventory.report.line"
    _description = "External Inventory Report Line"
    _check_company_auto = True
    _order = "id"

    report_id = fields.Many2one(
        "stock.external.inventory.report",
        required=True,
        ondelete="cascade",
        index=True,
        check_company=True,
    )
    company_id = fields.Many2one(
        "res.company", related="report_id.company_id", store=True
    )
    currency_id = fields.Many2one(
        "res.currency", related="report_id.currency_id", store=True
    )
    external_product_code = fields.Char(required=True, index=True)
    external_lot_name = fields.Char()
    external_date_mark = fields.Char()
    product_id = fields.Many2one("product.product", index=True, check_company=True)
    product_uom_id = fields.Many2one(related="product_id.uom_id", store=True)
    location_id = fields.Many2one("stock.location", index=True, check_company=True)
    lot_id = fields.Many2one("stock.lot", index=True, check_company=True)
    stock_type = fields.Char()
    external_qty = fields.Float(required=True, digits="Product Unit")
    odoo_qty = fields.Float(default=0.0, digits="Product Unit")
    delta_qty = fields.Float(
        compute="_compute_delta_qty", store=True, digits="Product Unit"
    )
    # Same type as ``standard_price``: unit costs go below the currency's cent,
    # which a Monetary field would round away when storing them.
    unit_cost = fields.Float(min_display_digits="Product Price", default=0.0)
    variance_amount = fields.Monetary(
        compute="_compute_variance_amount", store=True, currency_field="currency_id"
    )
    over_threshold = fields.Boolean(compute="_compute_flags", store=True)
    zero_standard_price = fields.Boolean(compute="_compute_flags", store=True)
    product_not_found = fields.Boolean(default=False, copy=False)
    line_state = fields.Selection(
        [
            ("new", "New"),
            ("reviewed", "Reviewed"),
            # TODO check if we may need to obsolete on line (EG: product removed)
            ("applied", "Applied"),
        ],
        default="new",
        required=True,
        copy=False,
    )
    reviewed_at = fields.Datetime(copy=False)
    note = fields.Char()

    @api.depends("external_qty", "odoo_qty")
    def _compute_delta_qty(self):
        for line in self:
            line.delta_qty = line.external_qty - line.odoo_qty

    @api.depends("delta_qty", "unit_cost")
    def _compute_variance_amount(self):
        for line in self:
            line.variance_amount = line.delta_qty * line.unit_cost

    @api.depends("variance_amount", "unit_cost")
    def _compute_flags(self):
        threshold = self.env[
            "stock.external.inventory.report"
        ]._get_discrepancy_threshold()
        for line in self:
            line.over_threshold = abs(line.variance_amount) > threshold
            # The cost is copied as is from the product, so a missing cost is
            # exactly zero.
            line.zero_standard_price = not line.unit_cost

    @api.model_create_multi
    def create(self, vals_list):
        self._normalize_input_vals(vals_list)
        self._populate_snapshot_fields(vals_list)
        lines = super().create(vals_list)
        return lines

    def write(self, vals):
        blocked = self.filtered(lambda rec: rec.report_id.state == "obsolete")
        if blocked:
            raise UserError(
                self.env._(
                    "Lines linked to obsolete inventory reports cannot be modified."
                )
            )

        if (
            any(
                key in vals
                for key in ("external_qty", "external_product_code", "stock_type")
            )
            and "line_state" not in vals
        ):
            vals = dict(vals, line_state="new", reviewed_at=False)

        self._normalize_input_vals([vals])

        result = super().write(vals)
        reports = self.report_id
        reports._sync_state_with_lines()
        return result

    def action_mark_reviewed(self):
        self = self._resolve_active_domain_fallback()
        for line in self:
            if line.report_id.state == "obsolete":
                raise UserError(
                    self.env._("You cannot review lines from an obsolete report.")
                )
            line.write({"line_state": "reviewed", "reviewed_at": fields.Datetime.now()})
        return True

    def action_apply_stock_overwrite(self):
        self = self._resolve_active_domain_fallback()

        skipped = []
        for line in self:
            if line.line_state == "applied":
                continue
            if line.report_id.state == "obsolete":
                raise UserError(
                    self.env._(
                        "You cannot apply stock overwrite from an obsolete report."
                    )
                )
            if not line.product_id or not line.location_id:
                skipped.append(
                    (
                        line,
                        self.env._(
                            "Code %(code)s is not resolved yet (no product/"
                            "location). Run the comparison first.",
                            code=line.external_product_code or self.env._("(unknown)"),
                        ),
                    )
                )
                continue
            if float_is_zero(
                line.delta_qty,
                precision_rounding=line.product_uom_id.rounding or 0.01,
            ):
                line.write(
                    {
                        "line_state": "reviewed",
                        "reviewed_at": fields.Datetime.now(),
                    }
                )
                continue

            line._apply_inventory_adjustment()
            line.write({"line_state": "applied", "reviewed_at": fields.Datetime.now()})

        reports = self.report_id
        reports._schedule_discrepancy_activities()
        reports._sync_state_with_lines()
        return self._build_skip_notification(
            skipped, self.env._("Apply Stock Overwrite")
        )

    def _resolve_active_domain_fallback(self):
        """Fall back to the list view's current search domain when a bulk
        header button (``display="always"``) is triggered with no row
        selected. Only triggers when ``active_domain`` is explicitly present
        in the context (always set by such buttons, even to an empty list) so
        that other callers passing an empty recordset without that context
        key (e.g. the report-level "Apply Stock Overwrite" button, which
        already pre-filters its target lines) remain unaffected no-ops.
        """
        if not self and "active_domain" in self.env.context:
            return self.search(self.env.context["active_domain"])
        return self

    def _build_skip_notification(self, skipped, action_label):
        if not skipped:
            return True
        lines_text = "\n".join(
            self.env._(
                "%(code)s (line #%(id)s): %(reason)s",
                code=line.external_product_code or self.env._("(unknown)"),
                id=line.id,
                reason=reason,
            )
            for line, reason in skipped
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._(
                    "%(action)s: %(count)s line(s) skipped",
                    action=action_label,
                    count=len(skipped),
                ),
                "message": lines_text,
                "type": "warning",
                "sticky": True,
            },
        }

    def _apply_inventory_adjustment(self):
        self.ensure_one()
        quant = self._get_inventory_adjustment_quant()
        quant.inventory_quantity = self.external_qty
        quant.user_id = self.env.user.id
        quant.action_apply_inventory()

    def _get_inventory_adjustment_quant(self):
        self.ensure_one()
        quant_model = self.env["stock.quant"].with_context(inventory_mode=True)
        quant = quant_model._gather(
            self.product_id,
            self.location_id,
            lot_id=self.lot_id or False,
            strict=True,
        )
        if quant:
            return quant[:1]
        return quant_model.create(
            {
                "product_id": self.product_id.id,
                "location_id": self.location_id.id,
                "lot_id": self.lot_id.id or False,
                "inventory_quantity": 0.0,
            }
        )

    @api.model
    def _populate_snapshot_fields(self, vals_list):
        product_model = self.env["product.product"]
        quant_model = self.env["stock.quant"]
        for vals in vals_list:
            if not vals.get("product_id") and vals.get("external_product_code"):
                company_id = vals.get("company_id") or self.env.company.id
                vals["product_id"] = product_model.search(
                    [
                        ("default_code", "=", vals["external_product_code"]),
                        ("company_id", "in", [company_id, False]),
                    ],
                    limit=1,
                ).id
            if vals.get("odoo_qty") is None:
                vals["odoo_qty"] = self._get_odoo_qty_snapshot(quant_model, vals)
            if vals.get("unit_cost") is None and vals.get("product_id"):
                vals["unit_cost"] = product_model.browse(
                    vals["product_id"]
                ).standard_price

    @api.model
    def _get_odoo_qty_snapshot(self, quant_model, vals):
        if not vals.get("product_id") or not vals.get("location_id"):
            return 0.0
        quants = quant_model.search(
            [
                ("product_id", "=", vals["product_id"]),
                ("location_id", "=", vals["location_id"]),
                ("company_id", "=", vals.get("company_id") or self.env.company.id),
                ("lot_id", "=", vals.get("lot_id") or False),
            ]
        )
        return sum(quants.mapped("quantity"))

    @api.model
    def _normalize_input_vals(self, vals_list):
        for vals in vals_list:
            if vals.get("product_id") and not vals.get("external_product_code"):
                vals["external_product_code"] = (
                    self.env["product.product"].browse(vals["product_id"]).default_code
                )
            if vals.get("lot_id") and not vals.get("external_lot_name"):
                vals["external_lot_name"] = (
                    self.env["stock.lot"].browse(vals["lot_id"]).name
                )

    def _resolve_external_values(self, warehouse):
        """Find the product, lot, location and Odoo stock of the new lines."""
        product_model = self.env["product.product"]
        lot_model = self.env["stock.lot"]
        quant_model = self.env["stock.quant"]
        for line in self.filtered(lambda rec: rec.line_state == "new"):
            product = product_model.search(
                [
                    ("default_code", "=", line.external_product_code),
                    ("company_id", "in", [line.company_id.id, False]),
                ],
                limit=1,
            )
            if not product:
                line.write(
                    {
                        "product_not_found": True,
                        "note": self.env._(
                            "Product not found for code %(code)s during the "
                            "comparison.",
                            code=line.external_product_code,
                        ),
                    }
                )
                continue

            location = line._get_location_from_stock_type(warehouse, line.stock_type)

            lot = self.env["stock.lot"]
            if line.external_lot_name:
                lot = lot_model.search(
                    [
                        ("product_id", "=", product.id),
                        ("name", "=", line.external_lot_name),
                    ],
                    limit=1,
                )
                if not lot:
                    lot = lot_model.create(
                        {"product_id": product.id, "name": line.external_lot_name}
                    )

            vals = {
                "product_not_found": False,
                "product_id": product.id,
                "location_id": location.id,
                "lot_id": lot.id if lot else False,
                "odoo_qty": line._get_odoo_qty_snapshot(
                    quant_model,
                    {
                        "product_id": product.id,
                        "location_id": location.id,
                        "company_id": line.company_id.id,
                        "lot_id": lot.id if lot else False,
                    },
                ),
                "unit_cost": product.standard_price,
            }
            if line.external_date_mark:
                vals["note"] = self.env._("date_mark=%s", line.external_date_mark)
            line.write(vals)

    def _get_location_from_stock_type(self, warehouse, stock_type):
        """Return the warehouse location of a stock type of the report."""
        return warehouse._get_stock_type_location(
            self._normalize_stock_type(stock_type)
        )

    def _normalize_stock_type(self, stock_type):
        """Return the warehouse stock type of a stock type of the report.

        Empty means free stock. Override it when the external system names the
        stock types otherwise.
        """
        return (stock_type or "").strip().lower() or STOCK_TYPE_FREE

    @api.ondelete(at_uninstall=False)
    def _unlink_except_obsolete_report_lines(self):
        blocked = self.filtered(lambda rec: rec.report_id.state == "obsolete")
        if blocked:
            raise UserError(
                self.env._("Lines linked to obsolete reports cannot be deleted.")
            )

    def unlink(self):
        reports = self.report_id
        result = super().unlink()
        reports._schedule_discrepancy_activities()
        reports._sync_state_with_lines()
        return result
