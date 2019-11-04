# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_pull(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        values,
    ):
        if (
            not self.env.context.get("_rule_no_available_defer")
            and self.route_id.available_to_promise_defer_pull
            # We still want to create the first part of the chain
            and not self.picking_type_id.code == "outgoing"
        ):
            moves = values.get("move_dest_ids")
            # track the moves that needs to have their pull rule
            # done
            if moves:
                moves.write({"need_rule_pull": True})
            return True

        super()._run_pull(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            values,
        )
        moves = values.get("move_dest_ids")
        if moves:
            moves.filtered(lambda r: r.need_rule_pull).write(
                {"need_rule_pull": False}
            )
        return True


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run_defer(
        self, product_id, product_qty, product_uom, location_id, origin, values
    ):
        values.setdefault(
            "company_id",
            self.env["res.company"]._company_default_get("procurement.group"),
        )
        values.setdefault("priority", "1")
        values.setdefault("date_planned", fields.Datetime.now())
        rule = self._get_rule(product_id, location_id, values)
        if not rule or rule.action not in ("pull", "pull_push"):
            return

        rule.with_context(_rule_no_available_defer=True)._run_pull(
            product_id,
            product_qty,
            product_uom,
            location_id,
            rule.name,
            origin,
            values,
        )
        return True
