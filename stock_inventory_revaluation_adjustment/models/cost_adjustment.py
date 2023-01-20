# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero

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
            ("confirm", "In Progress"),
            ("computing", "Computing"),
            ("done", "Validated"),
            ("posted", "Posted"),
            ("cancel", "Canceled"),
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
        domain="[('type', '!=', 'consu')]",
        help="Specify Products to focus your cost adjustment on particular Products. ",
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

    def _remove_unchanged_lines(self):
        precision = self.env["decimal.precision"].precision_get("Product Price")
        for line in self.line_ids:
            if float_is_zero(
                line.difference_cost,
                precision_digits=precision,
            ):
                line.unlink()
        if not self.line_ids:
            raise UserError(
                _("Nothing to do! At least one product should have a proposed cost.")
            )

    def action_validate(self):
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
            line.product_id.standard_price = line.product_cost
            line.product_id.proposed_cost = 0.0
        self.write({"state": "posted", "date": fields.Datetime.now()})
        return True

    def action_cancel(self):
        todo = self.filtered(lambda x: x.state not in ["posted"])
        todo.line_ids.unlink()
        todo.write({"state": "cancel"})

    def action_draft(self):
        todo = self.filtered(lambda x: x.state not in ["posted"])
        todo.line_ids.unlink()
        todo.write({"state": "draft"})

    def action_start(self):
        self.ensure_one()
        self.state = "computing"
        self._action_start()
        return True

    def action_reload(self):
        return True

    def _action_start(self):
        # To use Job Queue, post this method to the Queue
        todo = self.filtered(
            lambda x: x.product_ids and x.state in ["draft", "computing", "confirm"]
        )
        for adjustment in todo:
            adjustment.line_ids.unlink()
            adjustment._populate_adjustment_lines(adjustment.product_ids)
            adjustment.write({"state": "confirm", "date": fields.Datetime.now()})

    def _populate_adjustment_lines(self, products):
        """
        Given a list of Products
        Creates Adjustment Lines for the ones missing
        If a line aready exists, don't create a duplicate
        """
        self.ensure_one()
        missing = products - self.line_ids.product_id
        vals = [self._prepare_adjustment_line_values(x) for x in missing]
        return vals and self.line_ids.create(vals) or []

    def _prepare_adjustment_line_values(self, product):
        """
        Return the values of the lines to create for this cost adjustment.
        :return: a list containing the `stock.cost.adjustment.line` values to create
        :rtype: list
        """
        self.ensure_one()
        return {
            "cost_adjustment_id": self.id,
            "product_id": product.id,
            "product_original_cost": product.standard_price,
            "product_cost": product.proposed_cost or product.standard_price,
            "qty_on_hand": product.sudo().quantity_svl,
        }

    def action_open_cost_adjustment_lines(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Cost Adjustment Lines"),
            "res_model": "stock.cost.adjustment.line",
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
