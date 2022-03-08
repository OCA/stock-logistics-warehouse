# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CostAdjustmentLine(models.Model):
    _inherit = "cost.adjustment.line"

    mrp_production_ids = fields.Many2many(
        "mrp.production",
        string="Impacted MOs List",
        compute="_compute_set_productions_boms",
    )
    production_count = fields.Integer(
        string="Impacted MOs",
        compute="_compute_set_productions_boms",
        help="MOs this item is used on",
    )
    bom_ids = fields.Many2many(
        "mrp.bom", string="Impacted BOMs List", compute="_compute_set_productions_boms"
    )
    bom_count = fields.Integer(
        string="Impacted BOMs",
        compute="_compute_set_productions_boms",
        help="Bills of Materials this item is used on",
    )

    @api.depends("product_id")
    def _compute_set_productions_boms(self):
        Production = self.env["mrp.production"]
        BOM = self.env["mrp.bom"]
        for line in self:
            product = line.product_id
            if product:
                # List MOs where Product is used as s raw material
                productions1_domain = [
                    ("state", "in", ["draft", "confirmed", "progress"]),
                    ("move_raw_ids.product_id", "=", product.id),
                ]
                productions1 = Production.search(productions1_domain)
                # List MOs with a Work Center using Product as a Cost Type
                productions2_domain = [
                    ("state", "in", ["draft", "confirmed", "progress"]),
                    (
                        "workorder_ids.workcenter_id.analytic_product_id",
                        "=",
                        product.id,
                    ),
                ]
                productions2 = Production.search(productions2_domain)

                # List MOs with a Work Center using Product as a Cost Type Driver
                productions3_domain = [
                    ("state", "in", ["draft", "confirmed", "progress"]),
                    (
                        "workorder_ids.workcenter_id.analytic_product_id.activity_cost_ids",
                        "=",
                        product.id,
                    ),
                ]
                productions3 = Production.search(productions3_domain)

                line.mrp_production_ids = productions1 | productions2 | productions3
                line.production_count = len(line.mrp_production_ids)

                # FIXME: move to a module to remove MRP Analytic Dependency!
                # List BOMs where Product is used as a raw material
                boms1_domain = [("bom_line_ids.product_id", "=", product.id)]
                boms1 = BOM.search(boms1_domain)
                # List BOMs with a Workcenter using the Product as a Cost Type
                boms2_domain = [
                    (
                        "operation_ids.workcenter_id.analytic_product_id",
                        "=",
                        product.id,
                    ),
                ]
                boms2 = BOM.search(boms2_domain)
                # List BOMs with a Workcenter using the Product as a Cost Type Driver
                boms3_domain = [
                    (
                        "operation_ids.workcenter_id.analytic_product_id.activity_cost_ids",
                        "=",
                        product.id,
                    ),
                ]
                boms3 = BOM.search(boms3_domain)

                line.bom_ids = boms1 | boms2 | boms3
                line.bom_count = len(line.bom_ids)
            else:
                line.mrp_production_ids = None
                line.production_count = 0
                line.bom_ids = None
                line.bom_count = 0

    def action_view_production(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_production_action")
        action["domain"] = [("id", "in", self.mrp_production_ids.ids)]
        action["context"] = dict(self._context, create=False)
        return action

    def action_view_bom(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.product_open_bom")
        action["domain"] = [("id", "in", self.bom_ids.ids)]
        action["context"] = dict(self._context, create=False)
        return action
