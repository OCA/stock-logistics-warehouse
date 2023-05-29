# Copyright 2022 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


# TODO: move to its own file
class WorkCenter(models.Model):
    _inherit = "mrp.workcenter"

    def _get_rollup_cost(self):
        return self.costs_hour


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    unit_cost = fields.Float(
        string="Unit Cost",
    )

    operation_info_ids = fields.One2many(
        "operation.information",
        "operation_id",
        string="Operation Information",
    )
    cost_roll_up_version = fields.Boolean(related="bom_id.cost_roll_up_version", store=True)

    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            if rec.workcenter_id.costs_hour:
                rec.write({"unit_cost": rec.workcenter_id.costs_hour})

    def _compute_line_subtotal(self):
        for rec in self:
            rec.subtotal = (
                (rec.time_cycle_manual and rec.time_cycle_manual / 60) * rec.unit_cost
            ) or 0

    subtotal = fields.Float(compute="_compute_line_subtotal")


class OperationInformation(models.Model):
    _name = "operation.information"

    operation_id = fields.Many2one(
        "mrp.routing.workcenter",
        string="Operation",
    )
    analytic_product_id = fields.Many2one(
        "product.product",
        string="Cost type product",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Activity Cost Driver",
    )
    standard_price = fields.Float(
        string="Unit Cost",
    )
    factor = fields.Float(
        string="Qty factor",
    )

    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.standard_price * rec.factor

    subtotal = fields.Float(compute="_compute_subtotal")
