# Copyright 2021-2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class CostAdjustment(models.Model):
    _inherit = "stock.cost.adjustment"

    bom_impact_ids = fields.One2many(
        "stock.cost.adjustment.detail",
        "cost_adjustment_id",
        string="BoM Impact",
        copy=False,
        states={"done": [("readonly", True)]},
    )
    qty_impact_ids = fields.One2many(
        "stock.cost.adjustment.qty.impact.line",
        "cost_adjustment_id",
        string="Stock Qty. Impact",
        copy=False,
        states={"done": [("readonly", True)]},
    )

    def action_open_cost_adjustment_details(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Cost Adjustment Detail"),
            "res_model": "stock.cost.adjustment.detail",
            "context": {
                "default_is_editable": False,
                "default_cost_adjustment_id": self.id,
                "default_company_id": self.company_id.id,
                "search_default_group_by_bom_id": 1,
            },
            "domain": [("cost_adjustment_id", "=", self.id)],
            "view_id": self.env.ref(
                "stock_inventory_revaluation_mrp.cost_adjustment_detail_mrp_view_tree"
            ).id,
        }

    def action_open_cost_adjustment_details_qty(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("QTY On Hand Impact"),
            "res_model": "stock.cost.adjustment.qty.impact.line",
            "context": {
                "default_is_editable": False,
                "default_cost_adjustment_id": self.id,
                "default_company_id": self.company_id.id,
            },
            "domain": [("cost_adjustment_id", "=", self.id)],
            "view_id": self.env.ref(
                "stock_inventory_revaluation_mrp.cost_adjustment_qty_detail_mrp_view_tree"
            ).id,
        }

    def action_compute_impact(self):
        self.compute_impact()

    def compute_impact(self):
        self.bom_impact_ids.unlink()
        self.qty_impact_ids.unlink()
        self._populate_bom_impact_details(self.line_ids.product_id)
        cost_detail_obj = self.env["stock.cost.adjustment.detail"]
        qty_impact_obj = self.env["stock.cost.adjustment.qty.impact.line"]
        prod_detail_lines_bom = cost_detail_obj.search(
            [
                ("cost_adjustment_id", "=", self.id),
                ("bom_product_qty_on_hand", ">", 0.0),
            ]
        )
        for bom in prod_detail_lines_bom.mapped("bom_id"):
            if not qty_impact_obj.search(
                [("bom_id", "=", bom.id), ("cost_adjustment_id", "=", self.id)]
            ):
                if not bom.product_id:
                    bom_product_id = self.env["product.product"].search(
                        [
                            ("product_tmpl_id", "=", bom.product_tmpl_id.id),
                            ("type", "in", ["product", "consu"]),
                        ],
                        limit=1,
                    )
                else:
                    bom_product_id = bom.product_id

                current_cost = sum(
                    [
                        i.current_bom_cost
                        for i in prod_detail_lines_bom.filtered(
                            lambda a: a.bom_id == bom
                        )
                    ]
                )
                future_cost = sum(
                    [
                        i.future_bom_cost
                        for i in prod_detail_lines_bom.filtered(
                            lambda a: a.bom_id == bom
                        )
                    ]
                )
                qty_impact_obj.create(
                    {
                        "cost_adjustment_id": self.id,
                        "bom_id": bom.id,
                        "product_id": bom_product_id.id,
                        "qty_on_hand": bom_product_id.qty_available,
                        "product_original_cost": current_cost,
                        "product_cost": future_cost,
                    }
                )

    def _populate_bom_impact_details(self, products):
        """
        Populates BOM Impact lines (stock.cost.adjustment.detail)
        """
        if products:
            done_boms = self.bom_impact_ids.bom_id
            # BoMs impacted by component Products, not added yet
            boms = self._get_boms_impacted_products(products)
            self._create_cost_details(boms - done_boms)
            # Iterate on the next layer of Products impacted by the BOMs added
            impacted_products = self._get_products_for_boms(boms)
            self._populate_bom_impact_details(impacted_products - products)

    @api.model
    def _get_boms_impacted_products(self, products):
        """
        Return BOMs impacted by the give Products (components)

        BoMs for a Product Variant are only impacted by that Variant.
        BoMs for a Product Templates are impacted by any Variant.
        """
        product_ids = self.env["product.product"].search(
            [
                ("is_cost_type", "=", True),
                ("activity_cost_ids.product_id", "in", products.ids),
            ]
        )
        return self.env["mrp.bom"].search(
            [
                "|",
                ("bom_line_ids.product_id", "in", products.ids),
                (
                    "operation_ids.workcenter_id.analytic_product_id",
                    "in",
                    product_ids.ids,
                ),
            ]
        )

    @api.model
    def _get_products_for_boms(self, boms):
        """
        Return Products with BOM impact by given Products
        """
        variants = boms.product_id

        template_boms = boms.filtered(lambda x: not x.product_id)
        templates = template_boms.product_tmpl_id
        template_variants = templates.product_variant_ids
        return variants | template_variants

    def _create_cost_details(self, boms):
        cost_detail_obj = self.env["stock.cost.adjustment.detail"]
        cost_line_obj = self.env["stock.cost.adjustment.line"]
        for bom in boms.bom_line_ids:

            if not cost_detail_obj.search(
                [
                    ("bom_line_id", "=", bom.id),
                    ("cost_adjustment_id", "=", self.id),
                    ("bom_id", "=", bom.bom_id.id),
                    ("product_id", "=", bom.product_id.id),
                ]
            ):
                prod_line = cost_line_obj.search(
                    [
                        ("cost_adjustment_id", "=", self.id),
                        ("product_id", "=", bom.product_id.id),
                    ]
                )
                parent_bom = cost_detail_obj.search(
                    [
                        "|",
                        ("bom_id.product_id", "=", bom.product_id.id),
                        (
                            "bom_id.product_tmpl_id",
                            "=",
                            bom.product_id.product_tmpl_id.id,
                        ),
                        ("cost_adjustment_id", "=", self.id),
                    ]
                )
                if parent_bom:
                    future_cost = sum([a.future_bom_cost for a in parent_bom])
                else:
                    future_cost = (
                        prod_line.product_cost
                        if prod_line.product_id.id == bom.product_id.id
                        else bom.product_id.standard_price
                    )
                cost_detail_obj.create(
                    {
                        "product_id": bom.product_id.id,
                        "cost_adjustment_id": self.id,
                        "bom_line_id": bom.id,
                        "bom_id": bom.bom_id.id,
                        "quantity": bom.product_qty,
                        "product_original_cost": prod_line.product_original_cost
                        if prod_line.product_id.id == bom.product_id.id
                        else bom.product_id.standard_price,
                        "product_cost": future_cost,
                    }
                )

    def action_post(self):
        res = super().action_post()
        for line in self.line_ids:
            for bom in line.product_id.bom_line_ids.mapped("bom_id"):
                if bom.product_id:
                    bom.product_id.sudo().button_bom_cost()
                else:
                    bom.product_tmpl_id.sudo().button_bom_cost()
                for parent_bom in (
                    bom.product_id.bom_line_ids.mapped("bom_id")
                    if bom.product_id
                    else bom.product_tmpl_id.bom_line_ids.mapped("bom_id")
                ):
                    if parent_bom.product_id:
                        parent_bom.product_id.sudo().button_bom_cost()
                    else:
                        parent_bom.product_tmpl_id.sudo().button_bom_cost()
        return res
