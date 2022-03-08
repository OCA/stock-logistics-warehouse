# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class CostAdjustment(models.Model):
    _name = "stock.cost.adjustment"
    _description = "Cost Adjustment"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Reference",
        default="Cost Adjustment",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
    )
    date = fields.Datetime(
        string="Date",
        readonly=True,
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        help="""If the cost adjustment is not validated,
         date at which the cost adjustment was created.\n
        If the cost adjustment is validated, date at
         which the cost adjustment has been validated.""",
    )
    type_id = fields.Many2one(
        "stock.cost.adjustment.type",
        string="Type",
        required=True,
        states={"draft": [("readonly", False)]},
    )
    account_id = fields.Many2one(
        "account.account",
        string="Account",
        related="type_id.account_id",
    )
    line_ids = fields.One2many(
        "stock.cost.adjustment.line",
        "cost_adjustment_id",
        string="Inventories",
        copy=False,
        readonly=False,
        states={"done": [("readonly", True)]},
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("cancel", "Cancelled"),
            ("confirm", "In Progress"),
            ("done", "Validated"),
            ("posted", "Posted"),
        ],
        copy=False,
        index=True,
        readonly=True,
        tracking=True,
        default="draft",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        readonly=True,
        index=True,
        required=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.company,
    )
    product_ids = fields.Many2many(
        "product.product",
        string="Products",
        check_company=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('bom_ids','=',False)]",
        help="Specify Products to focus your cost adjustment on particular Products. ",
    )
    start_empty = fields.Boolean(
        "Empty Cost Adjustment", help="Allows to start with an empty cost adjustment."
    )

    def _check_negative(self):
        negative = next(
            (line for line in self.mapped("line_ids") if line.product_cost < 0),
            False,
        )
        if negative:
            raise UserError(
                _(
                    "You cannot set a negative product cost in a cost adjustment "
                    "line:\n\t%s - cost: %s",
                    negative.product_id.display_name,
                    negative.product_cost,
                )
            )
        return True

    def _remove_unchanged_lines(self):
        for line in self.line_ids:
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            if (
                float_compare(
                    line.product_cost,
                    line.product_original_cost,
                    precision_digits=precision,
                )
                == 0
            ):
                line.unlink()
        return True

    def action_validate(self):
        if not self.exists():
            return
        self.ensure_one()
        if not self.user_has_groups("stock.group_stock_manager"):
            raise UserError(_("Only a stock manager can validate a cost adjustment."))
        if self.state != "confirm":
            raise UserError(
                _(
                    "You can't validate the cost adjustment '%s', maybe this cost adjustment "
                    "has been already validated or isn't ready.",
                    self.name,
                )
            )
        self._check_negative()
        self._remove_unchanged_lines()
        self.write({"state": "done", "date": fields.Datetime.now()})
        return True

    def action_post(self):
        if not self.exists():
            return
        self.ensure_one()
        if not self.user_has_groups("stock.group_stock_manager"):
            raise UserError(_("Only a stock manager can post a cost adjustment."))
        if self.state != "done":
            raise UserError(
                _(
                    "You can't post the cost adjustment '%s', maybe this cost adjustment "
                    "has been already posted or isn't ready.",
                    self.name,
                )
            )
        self._check_negative()
        self._remove_unchanged_lines()
        for line in self.line_ids:
            line.product_id.write(
                {"standard_price": line.product_cost, "proposed_cost": 0.0}
            )
        self.write({"state": "posted", "date": fields.Datetime.now()})
        return True

    def action_cancel_draft(self):
        self.line_ids.unlink()
        self.write({"state": "draft"})

    def action_start(self):
        self.ensure_one()
        self._action_start()
        self._check_company()
        return self.action_open_cost_adjustment_lines()

    def _action_start(self):
        """Confirms the Cost Adjustment and generates its lines
        if its state is draft and don't have already lines (can happen
        with demo data or tests).
        """
        for adjustment in self:
            if adjustment.state != "draft":
                continue
            vals = {"state": "confirm", "date": fields.Datetime.now()}
            if not adjustment.line_ids and not adjustment.start_empty:
                self.env["stock.cost.adjustment.line"].create(
                    adjustment._get_cost_adjustment_lines_values()
                )
            adjustment.write(vals)

    def _get_cost_adjustment_lines_values(self):
        """Return the values of the lines to create for this cost adjustment.
        :return: a list containing the `stock.cost.adjustment.line` values to create
        :rtype: list
        """
        vals = []
        for product in self.product_ids:
            line_values = {
                "cost_adjustment_id": self.id,
                "product_id": product.id,
                "product_original_cost": product.standard_price,
                "product_cost": product.proposed_cost
                if product.proposed_cost > 0.0
                else product.standard_price,
                "qty_on_hand": product.sudo().quantity_svl,
            }
            vals.append(line_values)
        return vals

    def action_open_cost_adjustment_lines(self):
        self.ensure_one()
        ctx = dict(self._context) or {}
        ctx.update(
            {
                "default_is_editable": True,
                "default_cost_adjustment_id": self.id,
                "default_company_id": self.company_id.id,
            }
        )
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Cost Adjustment Lines"),
            "res_model": "stock.cost.adjustment.line",
            "context": ctx,
            "domain": [("cost_adjustment_id", "=", self.id)],
            "view_id": self.env.ref(
                "stock_inventory_revaluation_adjustment.cost_adjustment_line_view_tree"
            ).id,
        }
        return action

    def unlink(self):
        is_uninstall = self.env.context.get(MODULE_UNINSTALL_FLAG)
        for adjustment in self:
            if adjustment.state not in ("draft", "cancel") and not is_uninstall:
                raise UserError(
                    _(
                        "You can only delete a draft cost adjustment. "
                        "If the cost adjustment is not done, you can cancel it."
                    )
                )
        return super().unlink()
