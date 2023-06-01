# Copyright 2021-2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


class BoM(models.Model):
    _inherit = "mrp.bom"

    def get_produced_items(self):
        """
        Returns the Products Variants produced by a BoM
        """
        variants = self.product_id

        template_boms = self.filtered(lambda x: not x.product_id)
        templates = template_boms.product_tmpl_id
        template_variants = templates.product_variant_ids
        return variants | template_variants

    active_ref_bom = fields.Boolean(string="Active Reference BOM")
    cost_roll_up_version = fields.Boolean(string="Cost Roll Version", default=False)

    def _compute_material_total_cost(self):
        for rec in self:
            rec.material_total_cost = sum(mtl.subtotal for mtl in rec.bom_line_ids)

    material_total_cost = fields.Float(compute="_compute_material_total_cost")
    
    def _compute_operation_total_cost(self):
        for rec in self:
            rec.operation_total_cost = sum(opt.subtotal for opt in rec.operation_ids)

    operation_total_cost = fields.Float(compute="_compute_operation_total_cost")

    def copy(self, default=None):
        # cost roll version, no copies allowed
        if self.cost_roll_up_version and not self.env.context.get('allow', False):
            raise ValidationError(_("You cannot duplicate Cost Roll Version BOM"))
        else:
            return super().copy(default)

    def unlink(self):
        # cost roll version, deletion not allowed
        if self.cost_roll_up_version and not self.env.context.get('allow', False):
            raise ValidationError(_("You cannot delete Cost Roll Version BOM"))
        else:
            return super().unlink()

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.cost_roll_up_version and vals and not self._context.get('bypass_checks'):
                raise ValidationError(_("You cannot update cost roll BOM"))

            if vals.get("active") and rec.cost_roll_up_version:
                raise ValidationError(_("You cannot active Cost Roll Version BOM"))
        return res

    def update_bom_version(self):
        bom_obj = self.env["mrp.bom"]
        no_of_bom_version = self.env.company.no_of_bom_version
        for bom in self:
            version_boms = bom_obj.search(
                [
                    ("product_tmpl_id", "=", bom.product_tmpl_id.id),
                    ("active", "=", False),
                    ("cost_roll_up_version", "=", True)
                ],
                order="id ASC",
            )
            version_boms.filtered(lambda l: l.active_ref_bom == True).with_context(bypass_checks=True).write({"active_ref_bom": False})
            if version_boms and len(version_boms) >= no_of_bom_version:
                limit = (len(version_boms) - no_of_bom_version)
                unlink_boms = version_boms[0:limit+1]
                unlink_boms.with_context(allow=True).unlink()
            new_bom = bom.copy(
                {
                  "active": False,
                  "active_ref_bom": True,
                  "cost_roll_up_version": True,
                }
            )
            for line in new_bom.bom_line_ids:
                line.write({"unit_cost": line.product_id.standard_price})
            for operatine in new_bom.operation_ids.filtered(
                lambda l: l.workcenter_id.analytic_product_id.activity_cost_ids
            ):
                activity_cost_ids = []
                for (
                    activity
                ) in operatine.workcenter_id.analytic_product_id.activity_cost_ids:
                    activity_cost_ids.append(
                        (
                            0,
                            0,
                            {
                                "analytic_product_id": operatine.workcenter_id.analytic_product_id.id,
                                "product_id": activity.product_id.id,
                                "standard_price": activity.standard_price,
                                "factor": activity.factor,
                            },
                        )
                    )
                if activity_cost_ids:
                    operatine.write({"operation_info_ids": activity_cost_ids})


class BomLine(models.Model):
    _inherit = "mrp.bom.line"

    unit_cost = fields.Float()

    def _compute_line_subtotal(self):
        for rec in self:
            subtotal = 0.0
            if rec.bom_id.cost_roll_up_version:
                subtotal = rec.product_qty * rec.unit_cost
            rec.subtotal = subtotal

    subtotal = fields.Float(compute="_compute_line_subtotal")


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_bom(
        self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False
    ):
        res = super(ReportBomStructure, self)._get_bom(
            bom_id, product_id, line_qty, line_id, level
        )
        res["proposed_cost"] = res["product"].proposed_cost
        return res

    @api.model
    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        res = super(ReportBomStructure, self)._get_bom_lines(
            bom, bom_quantity, product, line_id, level
        )
        for line in res[0]:
            product_id = self.env["product.product"].browse([line["prod_id"]])
            line["proposed_cost"] = product_id.proposed_cost

        return res
