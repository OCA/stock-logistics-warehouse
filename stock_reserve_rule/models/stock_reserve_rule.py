# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


def _default_sequence(record):
    maxrule = record.search([], order="sequence desc", limit=1)
    if maxrule:
        return maxrule.sequence + 10
    else:
        return 0


class StockReserveRule(models.Model):
    """Rules for stock reservations

    Each rule can have many removal rules, they configure the conditions and
    advanced removal strategies to apply on a specific location (sub-location
    of the rule).

    The rules are selected for a move based on their source location and a
    configurable domain on the rule.
    """

    _name = "stock.reserve.rule"
    _description = "Stock Reservation Rule"
    _order = "sequence, id"

    name = fields.Char(string="Description", required=True)
    sequence = fields.Integer(default=lambda s: _default_sequence(s))
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.user.company_id.id
    )

    location_id = fields.Many2one(
        comodel_name="stock.location",
        required=True,
        help="Rule applied only in this location and sub-locations.",
    )
    picking_type_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        string="Operation Types",
        help="Apply this rule only if the operation type of the move is the same.",
    )

    rule_removal_ids = fields.One2many(
        comodel_name="stock.reserve.rule.removal", inverse_name="rule_id"
    )

    rule_domain = fields.Char(
        string="Rule Domain",
        default=[],
        help="Domain based on Stock Moves, to define if the "
        "rule is applicable or not.",
    )

    def _rules_for_location(self, location):
        return self.search([("location_id", "parent_of", location.id)])

    def _eval_rule_domain(self, move, domain):
        move_domain = [("id", "=", move.id)]
        # Warning: if we build a domain with dotted path such
        # as group_id.is_urgent (hypothetic field), can become very
        # slow as odoo searches all "procurement.group.is_urgent" first
        # then uses "IN group_ids" on the stock move only.
        # In such situations, it can be better either to add a related
        # field on the stock.move, either extend _eval_rule_domain to
        # add your own logic (based on SQL, ...).
        return bool(
            self.env["stock.move"].search(
                expression.AND([move_domain, domain]), limit=1
            )
        )

    def _is_rule_applicable(self, move):
        if self.picking_type_ids:
            picking_type = move.picking_type_id or move.picking_id.picking_type_id
            if picking_type not in self.picking_type_ids:
                return False
        domain = safe_eval(self.rule_domain) or []
        if domain:
            return self._eval_rule_domain(move, domain)
        return True


class StockReserveRuleRemoval(models.Model):
    """Rules for stock reservations removal

    A removal rule does:

    * Filter quants that a removal rule can reserve for the location
      (_filter_quants)
    * An advanced removal strategy for the preselected quants (_apply_strategy)

    New advanced removal strategies can be added by other modules, see the
    method ``_apply_strategy`` and the default methods for more documentation
    about their contract.
    """

    _name = "stock.reserve.rule.removal"
    _description = "Stock Reservation Rule Removal"
    _order = "sequence, id"

    rule_id = fields.Many2one(
        comodel_name="stock.reserve.rule", required=True, ondelete="cascade"
    )
    name = fields.Char(string="Description")
    location_id = fields.Many2one(comodel_name="stock.location", required=True)

    sequence = fields.Integer(default=lambda s: _default_sequence(s))

    # quants exclusion
    quant_domain = fields.Char(
        string="Quants Domain",
        default=[],
        help="Filter Quants allowed to be reserved for this location "
        "and sub-locations.",
    )

    # advanced removal strategy
    removal_strategy = fields.Selection(
        string="Advanced Removal Strategy",
        selection=[
            ("default", "Default Removal Strategy"),
            ("empty_bin", "Empty Bins"),
            ("packaging", "Full Packaging"),
            ("full_bin", "Full Bin"),
            ("full_lot", "Full Lot"),
        ],
        required=True,
        default="default",
        help="Defines if and how goods are taken from locations."
        "Default: take the first ones with the configured Removal Strategy"
        "(FIFO, FEFO, ...).\n"
        "Empty Bins: take goods from a location only if the bin is"
        " empty afterwards.\n"
        "Full Packaging: take goods from a location only if the location "
        "quantity matches a packaging quantity (do not open boxes).\n"
        "Full Bin: take goods from a location if it reserves all its content"
        "quantity matches a packaging quantity (do not open boxes)."
        "By lot: ",
    )

    packaging_type_ids = fields.Many2many(
        comodel_name="product.packaging.type",
        help="Optional packaging when using 'Full Packaging'.\n"
        "Only the quantities matching one of the packaging are removed.\n"
        "When empty, any packaging can be removed.",
    )

    TOLERANCE_LIMIT = [
        ("no_tolerance", "No tolerance"),
        ("upper_limit", "Upper Limit"),
        ("lower_limit", "Lower Limit"),
    ]

    tolerance_requested_limit = fields.Selection(
        selection=TOLERANCE_LIMIT,
        string="Tolerance on",
        help="Selecting a tolerance limit type"
        "No tolerance: lot qty should be equal required"
        "Upper Limit: quantity higher than demand but within tolerance"
        "Lower Limit: lot with lower qty than required",
        default="no_tolerance",
        required=True,
    )

    tolerance_requested_computation = fields.Selection(
        selection=[
            ("percentage", "Percentage (%)"),
            ("absolute", "Absolute Value"),
        ],
        string="Tolerance computation",
        required=True,
        default="percentage",
    )

    tolerance_requested_value = fields.Float(string="Tolerance value", default=0.0)

    tolerance_display = fields.Char(
        compute="_compute_tolerance_display", store=True, string="Tolerance"
    )

    @api.depends(
        "tolerance_requested_limit",
        "tolerance_requested_computation",
        "tolerance_requested_value",
    )
    def _compute_tolerance_display(self):
        for rec in self:
            tolerance_on = rec.tolerance_requested_limit
            tolerance_computation = rec.tolerance_requested_computation
            value = rec.tolerance_requested_value
            if value == 0.0:
                rec.tolerance_display = "Requested Qty = Lot Qty"
                continue
            limit = "-" if tolerance_on == "lower_limit" else ""
            computation = "%" if tolerance_computation == "percentage" else ""
            tolerance_on_dict = dict(self.TOLERANCE_LIMIT)
            rec.tolerance_display = "{} ({}{}{})".format(
                tolerance_on_dict.get(tolerance_on), limit, value, computation
            )

    @api.onchange("tolerance_requested_value")
    def _onchange_tolerance_limit(self):
        if self.tolerance_requested_value < 0.0:
            raise models.UserError(
                _(
                    "Tolerance from requested qty value must be more than or equal to 0.0"
                )
            )

    @api.constrains("location_id")
    def _constraint_location_id(self):
        """The location has to be a child of the rule location."""
        for removal_rule in self:
            if not removal_rule.location_id.is_sublocation_of(
                removal_rule.rule_id.location_id
            ):
                msg = _(
                    "Removal rule '{}' location has to be a child "
                    "of the rule location '{}'."
                ).format(
                    removal_rule.name,
                    removal_rule.rule_id.location_id.display_name,
                )
                raise ValidationError(msg)

    def _eval_quant_domain(self, quants, domain):
        quant_domain = [("id", "in", quants.ids)]
        return self.env["stock.quant"].search(expression.AND([quant_domain, domain]))

    def _filter_quants(self, move, quants):
        domain = safe_eval(self.quant_domain) or []
        if domain:
            return self._eval_quant_domain(quants, domain)
        return quants

    def _apply_strategy(self, quants):
        """Apply the advanced removal strategy

        New methods can be added by:

        - Adding a selection in the 'removal_strategy' field.
        - adding a method named after the selection value
          (_apply_strategy_SELECTION)

        A strategy has to comply with this signature: (self, quants)
        Where 'self' is the current rule and 'quants' are the candidate
        quants allowed for the rule, sorted by the company's removal
        strategy (fifo, fefo, ...).
        It has to get the initial need using 'need = yield' once, then,
        each time the strategy decides to take quantities in a location,
        it has to yield and retrieve the remaining needed using:

            need = yield location, location_quantity, quantity_to_take, lot, owner

        See '_apply_strategy_default' for a short example.

        """
        method_name = "_apply_strategy_%s" % (self.removal_strategy)
        yield from getattr(self, method_name)(quants)

    def _apply_strategy_default(self, quants):
        need = yield
        # Propose quants in the same order than returned originally by
        # the _gather method, so based on fifo, fefo, ...
        for quant in quants:
            need = yield (
                quant.location_id,
                quant.quantity - quant.reserved_quantity,
                need,
                quant.lot_id,
                quant.owner_id,
            )

    def _apply_strategy_empty_bin(self, quants):
        need = yield
        # Group by location (in this removal strategies, we want to consider
        # the total quantity held in a location).
        quants_per_bin = quants._group_by_location()
        # We take goods only if we empty the bin.
        # The original ordering (fefo, fifo, ...) must be kept.
        product = fields.first(quants).product_id
        rounding = product.uom_id.rounding
        locations_with_other_quants = [
            group["location_id"][0]
            for group in quants.read_group(
                [
                    ("location_id", "in", quants.location_id.ids),
                    ("product_id", "not in", quants.product_id.ids),
                    ("quantity", ">", 0),
                ],
                ["location_id"],
                "location_id",
            )
        ]
        for location, location_quants in quants_per_bin:
            if location.id in locations_with_other_quants:
                continue

            location_quantity = sum(location_quants.mapped("quantity")) - sum(
                location_quants.mapped("reserved_quantity")
            )

            if location_quantity <= 0:
                continue

            if float_compare(need, location_quantity, rounding) != -1:
                need = yield location, location_quantity, need, None, None

    def _apply_strategy_packaging(self, quants):
        need = yield
        # Group by location (in this removal strategies, we want to consider
        # the total quantity held in a location).
        quants_per_bin = quants._group_by_location()

        product = fields.first(quants).product_id

        packaging_type_filter = self.packaging_type_ids

        # we'll walk the packagings from largest to smallest to have the
        # largest containers as possible (1 pallet rather than 10 boxes)
        packaging_quantities = sorted(
            product.packaging_ids.filtered(
                lambda packaging: (
                    packaging.qty > 0
                    and (
                        packaging.packaging_type_id in packaging_type_filter
                        if packaging_type_filter
                        else True
                    )
                )
            ).mapped("qty"),
            reverse=True,
        )

        rounding = product.uom_id.rounding

        def is_greater_eq(value, other):
            return float_compare(value, other, precision_rounding=rounding) >= 0

        for location, location_quants in quants_per_bin:
            location_quantity = sum(location_quants.mapped("quantity")) - sum(
                location_quants.mapped("reserved_quantity")
            )
            if location_quantity <= 0:
                continue

            for pack_quantity in packaging_quantities:
                enough_for_packaging = is_greater_eq(location_quantity, pack_quantity)
                asked_at_least_packaging_qty = is_greater_eq(need, pack_quantity)
                if enough_for_packaging and asked_at_least_packaging_qty:
                    # compute how much packaging we can get
                    take = (need // pack_quantity) * pack_quantity
                    need = yield location, location_quantity, take, None, None

    def _apply_strategy_full_bin(self, quants):
        need = yield
        # Only location with nothing reserved can be fully emptied
        quants = quants.filtered(lambda q: q.reserved_quantity == 0)
        # Group by location (in this removal strategies, we want to consider
        # the total quantity held in a location).
        quants_per_bin = quants._group_by_location()
        # We take goods only if we empty the bin.
        # The original ordering (fefo, fifo, ...) must be kept.
        product = fields.first(quants).product_id
        rounding = product.uom_id.rounding
        locations_with_other_quants = [
            group["location_id"][0]
            for group in quants.read_group(
                [
                    ("location_id", "in", quants.location_id.ids),
                    ("product_id", "not in", quants.product_id.ids),
                    ("quantity", ">", 0),
                ],
                ["location_id"],
                "location_id",
            )
        ]
        for location, location_quants in quants_per_bin:
            if location.id in locations_with_other_quants:
                continue

            location_quantity = sum(location_quants.mapped("quantity"))

            if location_quantity <= 0:
                continue

            if float_compare(need, location_quantity, rounding) != -1:
                need = yield location, location_quantity, need, None, None

    def _compare_with_tolerance(self, need, product_qty, rounding):
        tolerance = self.tolerance_requested_value
        limit = self.tolerance_requested_limit
        computation = self.tolerance_requested_computation
        if limit == "no_tolerance" or float_compare(tolerance, 0, rounding) == 0:
            return float_compare(need, product_qty, rounding) == 0
        elif limit == "upper_limit":
            if computation == "percentage":
                # need + rounding < product_qty <= need * (100 + tolerance) / 100
                return (
                    float_compare(need, product_qty, rounding) == -1
                    and float_compare(
                        product_qty, need * (100 + tolerance) / 100, rounding
                    )
                    <= 0
                )
            else:
                # need + rounding < product_qty <= need + tolerance
                return (
                    float_compare(need, product_qty, rounding) == -1
                    and float_compare(product_qty, need + tolerance, rounding) <= 0
                )
        elif limit == "lower_limit":
            if computation == "percentage":
                # need * (100 - tolerance) / 100 <= product_qty < need - rounding
                return (
                    float_compare(need * (100 - tolerance) / 100, product_qty, rounding)
                    <= 0
                    and float_compare(product_qty, need, rounding) == -1
                )
            # computation == "absolute"
            else:
                # need - tolerance <= product_qty < need - rounding
                return (
                    float_compare(need - tolerance, product_qty, rounding) <= 0
                    and float_compare(product_qty, need, rounding) == -1
                )

    def _apply_strategy_full_lot(self, quants):
        need = yield
        # We take goods only if we empty the bin.
        # The original ordering (fefo, fifo, ...) must be kept.
        product = fields.first(quants).product_id
        if product.tracking == "lot":
            rounding = product.uom_id.rounding
            for lot, lot_quants in quants.filtered(
                lambda quant: quant.product_id.id == product.id
                and quant.lot_id
                and not quant.reserved_quantity
            ).group_by_lot():
                product_qty = sum(lot_quants.mapped("quantity"))
                if not self._compare_with_tolerance(need, product_qty, rounding):
                    continue
                for lot_quant in lot_quants:
                    lot_quantity = lot_quant.quantity - lot_quant.reserved_quantity
                    need = yield (
                        lot_quant.location_id,
                        lot_quantity,
                        need,
                        lot,
                        None,
                    )
