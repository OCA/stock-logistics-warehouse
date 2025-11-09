# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero


class StockRule(models.Model):
    _inherit = "stock.rule"

    action = fields.Selection(
        selection_add=[("split_procurement", "Choose between MTS and MTO")],
        ondelete={"split_procurement": "cascade"},
    )
    mts_rule_id = fields.Many2one("stock.rule", string="MTS Rule", check_company=True)
    mto_rule_id = fields.Many2one("stock.rule", string="MTO Rule", check_company=True)

    def _run_subrule_action(self, procurement, subrule):
        """Shortcut to run a subrule for a single procurement."""
        self.ensure_one()
        run_subrule = getattr(self.env["stock.rule"], f"_run_{subrule.action}")
        return run_subrule([(procurement, subrule)])

    def _run_mts_action(self, procurement):
        """Shortcut to run the MTS rule linked to this MTS+MTO rule."""
        self.mts_rule_id.ensure_one()
        return self._run_subrule_action(procurement, self.mts_rule_id)

    def _run_mto_action(self, procurement):
        """Shortcut to run the MTO rule linked to this MTS+MTO rule."""
        self.mto_rule_id.ensure_one()
        return self._run_subrule_action(procurement, self.mto_rule_id)

    @api.constrains("action", "mts_rule_id", "mto_rule_id")
    def _check_mts_mto_rule(self):
        for rule in self:
            if rule.action == "split_procurement":
                if not rule.mts_rule_id or not rule.mto_rule_id:
                    msg = self.env._(
                        "No MTS or MTO rule configured on procurement rule: %s!"
                    ) % (rule.name,)
                    raise ValidationError(msg)
                # TODO: Check this
                # if (
                #     rule.mts_rule_id.location_src_id.id
                #     != rule.mto_rule_id.location_src_id.id
                # ):
                #     msg = self.env._(
                #         "Inconsistency between the source locations of "
                #         "the mts and mto rules linked to the procurement "
                #         "rule: %s! It should be the same."
                #     ) % (rule.name,)
                #     raise ValidationError(msg)

    def get_mto_qty_to_order(self, product, product_qty, product_uom, values):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        src_location_id = self.mts_rule_id.location_src_id.id
        product_location = product.with_context(location=src_location_id)
        virtual_available = product_location.virtual_available
        qty_available = product.uom_id._compute_quantity(virtual_available, product_uom)
        if float_compare(qty_available, 0.0, precision_digits=precision) > 0:
            if (
                float_compare(qty_available, product_qty, precision_digits=precision)
                >= 0
            ):
                return 0.0
            else:
                return product_qty - qty_available
        return product_qty

    def _run_split_procurement(self, procurements):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for procurement, rule in procurements:
            domain = self.env["procurement.group"]._get_moves_to_assign_domain(
                procurement.company_id.id
            )
            # Determine the quantity to order as MTO
            needed_qty = rule.get_mto_qty_to_order(
                procurement.product_id,
                procurement.product_qty,
                procurement.product_uom,
                procurement.values,
            )
            # Enough stock, only MTS
            if float_is_zero(needed_qty, precision_digits=precision):
                rule._run_mts_action(procurement)
            # No stock, only MTO
            elif (
                float_compare(
                    needed_qty, procurement.product_qty, precision_digits=precision
                )
                == 0.0
            ):
                rule._run_mto_action(procurement)
            # Partial stock, split between MTS and MTO
            else:
                mts_qty = procurement.product_qty - needed_qty
                mts_procurement = procurement._replace(product_qty=mts_qty)
                rule._run_mts_action(mts_procurement)

                # Search all confirmed stock_moves of mts_procurement and assign them
                # to adjust the product's free qty
                group_id = mts_procurement.values.get("group_id")
                # TODO: Check if this is necessary as moves are auto assigned
                if group_id:
                    group_domain = expression.AND(
                        [domain, [("group_id", "=", group_id.id)]]
                    )
                    moves_to_assign = self.env["stock.move"].search(
                        group_domain, order="priority desc, date asc"
                    )
                    moves_to_assign._action_assign()

                mto_procurement = procurement._replace(product_qty=needed_qty)
                rule._run_mto_action(mto_procurement)
        return True
