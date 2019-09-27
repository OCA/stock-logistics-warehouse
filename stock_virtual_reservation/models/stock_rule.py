# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = "stock.rule"

    # TODO add in view, visible when action is pull
    virtual_reservation_defer_pull = fields.Boolean(
        string="Defer Pull using Virtual Reservation",
        default=False,
        help="Create the pull moves only when the virtual "
        "reservation is > 0.",
    )

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
            not self.env.context.get("_rule_no_virtual_defer")
            and self.virtual_reservation_defer_pull
            and not self.picking_type_id.code == "outgoing"
        ):
            return True
        return super()._run_pull(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            values,
        )


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

        rule.with_context(_rule_no_virtual_defer=True)._run_pull(
            product_id,
            product_qty,
            product_uom,
            location_id,
            rule.name,
            origin,
            values,
        )
        return True
