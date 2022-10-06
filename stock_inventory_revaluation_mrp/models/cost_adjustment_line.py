# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CostAdjustmentLine(models.Model):
    _inherit = "stock.cost.adjustment.line"
    _order = "level,product_id"

    bom_impact_ids = fields.One2many(
        "stock.cost.adjustment.detail",
        "cost_adjustment_line_id",
        string="BoM Impact",
        copy=False,
        states={"done": [("readonly", True)]},
    )
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
    level = fields.Integer()

    def _get_impacted_mos(self):
        """
        List MOs where Product is used as raw material
        """
        domain = [
            ("state", "in", ["draft", "confirmed", "progress"]),
            ("move_raw_ids.product_id", "in", self.product_id.ids),
        ]
        return self.env["mrp.production"].search(domain)

    def _get_impacted_boms(self):
        """
        List BOMs where Product is used as a raw material
        """
        BOM = self.env["mrp.bom"]
        products = self.product_id
        boms1_domain = [("bom_line_ids.product_id", "in", products.ids)]
        boms1 = BOM.search(boms1_domain)
        # List BOMs with a Workcenter using the Product as a Cost Type
        boms2_domain = [
            ("operation_ids.workcenter_id.analytic_product_id", "in", products.ids)
        ]
        boms2 = BOM.search(boms2_domain)
        return boms1 | boms2

    @api.depends("product_id")
    def _compute_set_productions_boms(self):
        for line in self:
            if line.product_id:
                line.mrp_production_ids = line._get_impacted_mos()
                line.production_count = len(line.mrp_production_ids)
                line.bom_ids = line._get_impacted_boms()
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

    def _create_impacted_bom_lines(self):
        self and self.ensure_one()
        product = self.product_id
        level = self.level
        bom_lines = self.env["mrp.bom.line"].search([("product_id", "=", product.id)])
        vals = []
        for bom_line in bom_lines:
            impacted_products = bom_line.bom_id.get_produced_items()
            for impacted_product in impacted_products:
                add_cost = self.difference_cost * bom_line.product_qty
                vals.append(
                    {
                        "cost_adjustment_line_id": self.id,
                        "bom_line_id": bom_line.id,
                        "bom_id": bom_line.bom_id.id,
                        "product_id": impacted_product.id,
                        "quantity": bom_line.product_qty,
                        "cost_increase": add_cost,
                        "parent_product_id": product.id,
                        "level": level,
                    }
                )
        if vals:
            return self.env["stock.cost.adjustment.detail"].create(vals)
