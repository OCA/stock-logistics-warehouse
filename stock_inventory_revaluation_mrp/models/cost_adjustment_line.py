# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CostAdjustmentLine(models.Model):
    _inherit = "stock.cost.adjustment.line"

    @api.depends("state", "is_automatically_added")
    def _compute_is_editable(self):
        super()._compute_is_editable()
        for line in self:
            if line.is_automatically_added:
                line.is_editable = False

    is_automatically_added = fields.Boolean(
        help="Impacted Products are automatically added to the line list"
    )
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
    level = fields.Integer(string="Level")


    @api.depends("product_id")
    def _compute_set_productions_boms(self):
        Production = self.env["mrp.production"]
        BOM = self.env["mrp.bom"]
        for line in self:
            product = line.product_id
            if product:
                # List MOs where Product is used as raw material
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
                        "workorder_ids.workcenter_id.analytic_product_id"
                        ".activity_cost_ids.product_id",
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

    def _populate_bom_impact_details(self, products, level=1):
        """
        Populates BOM Impact lines (stock.cost.adjustment.detail)

        Cost Adjustment Lines are Products changing their cost.
        These Products can be used in BoMs and will then impact other Products.
        Impacted Products can also used in BoMs, and so impat further Products.

        For a Product list (initially the Cost Adjustment Line Product), explode the impacts:
        - Find the impacted BoMs
        - Find the impacted Product Variants
        - Write down the additional cost for these Variants, caused by the origin Products
        """
        _logger.info(
            "STARTING level %d impact for %d products...", level, len(products)
        )
        impacted_products = self.env["product.product"]
        for product in products:
            # Impact from BoM Line usage
            cost_details_add = self._create_impacted_bom_lines(product)
            if cost_details_add and len(cost_details_add) >= 100:
                _logger.info(
                    "... product %s added %d cost detail lines",
                    product.display_name,
                    cost_details_add and len(cost_details_add) or 0,
                )
            # Iterate on the next layer of Products impacted by the BOMs added
            if cost_details_add:
                impacted_products |= cost_details_add.product_id
        if impacted_products:
            self._populate_bom_impact_details(impacted_products, level=level + 1)

    def _create_impacted_bom_lines(self, product):
        self and self.ensure_one()
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
                    }
                )
        if vals:
            return self.env["stock.cost.adjustment.detail"].create(vals)

    def _populate_impacted_products(self):
        """
        Adds to the Adjustment Lines the Products that need cost adjustment
        because of impacted MRP BoMs.

        First the _populate_bom_impact_details() method finds all BoM Products
        impacted by cost changes in raw materials.
        Using these cost details, the new lines can be added.
        """
        impacted_products = self.bom_impact_ids.product_id
        existing_products = self.filtered("is_automatically_added").product_id
        # Delete automatic lines that are no longer needed
        obsolete_products = existing_products - impacted_products
        if obsolete_products:
            obsolete_lines = self.filtered(lambda x: x.product_id in obsolete_products)
            obsolete_lines.unlink()
        # Add new lines and update existing ones
        AdjustmentLine = self.env["stock.cost.adjustment.line"]
        new_lines = AdjustmentLine
        for product in impacted_products:
            impact_details = self.bom_impact_ids.filtered(
                lambda x: x.product_id == product
            )
            cost_increase = sum(impact_details.mapped("cost_increase"))
            product_cost = product.standard_price + cost_increase
            if product in existing_products:
                line = self.filtered(lambda x: x.product_id == product)
                line.product_cost = product_cost
                line.product_original_cost = product.standard_price
            else:
                vals = {
                    "cost_adjustment_id": self.cost_adjustment_id.id,
                    "product_id": product.id,
                    "product_original_cost": product.standard_price,
                    "product_cost": product_cost,
                    "is_automatically_added": True,
                }
                new_lines |= AdjustmentLine.create(vals)
        return new_lines
