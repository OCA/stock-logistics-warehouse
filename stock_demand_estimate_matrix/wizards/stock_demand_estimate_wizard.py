# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class DemandEstimateWizard(models.TransientModel):
    _name = "stock.demand.estimate.wizard"
    _description = "Stock Demand Estimate Wizard"

    date_start = fields.Date(
        string="Date From",
        required=True,
    )
    date_end = fields.Date(
        string="Date To",
        required=True,
    )
    date_range_type_id = fields.Many2one(
        string="Date Range Type",
        comodel_name="date.range.type",
        required=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location",
        required=True,
    )
    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products",
    )

    @api.onchange("date_range_type_id")
    def _onchange_date_range_type_id(self):
        if self.date_range_type_id.company_id:
            return {
                "domain": {
                    "location_id": [
                        ("company_id", "=", self.date_range_type_id.company_id.id)
                    ]
                }
            }
        return {}

    @api.constrains("date_start", "date_end")
    def _check_start_end_dates(self):
        self.ensure_one()
        if self.date_start > self.date_end:
            raise ValidationError(
                _("The start date cannot be later than the end date.")
            )

    def _prepare_demand_estimate_sheet(self):
        self.ensure_one()
        return {
            "date_start": self.date_start,
            "date_end": self.date_end,
            "date_range_type_id": self.date_range_type_id.id,
            "location_id": self.location_id.id,
        }

    def create_sheet(self):
        self.ensure_one()
        if not self.product_ids:
            raise UserError(_("You must select at least one product."))

        # 2d matrix widget need real records to work
        sheet = self.env["stock.demand.estimate.sheet"].create(
            {
                "date_start": self.date_start,
                "date_end": self.date_end,
                "date_range_type_id": self.date_range_type_id.id,
                "location_id": self.location_id.id,
                "product_ids": [(6, 0, self.product_ids.ids)],
            }
        )
        sheet._onchange_dates()

        res = {
            "name": _("Estimate Sheet"),
            "src_model": "stock.demand.estimate.wizard",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "res_model": "stock.demand.estimate.sheet",
            "res_id": sheet.id,
            "type": "ir.actions.act_window",
        }
        return res
