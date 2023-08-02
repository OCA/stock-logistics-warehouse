# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade_merge_records

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BaseProductUomMerge(models.TransientModel):
    _name = "base.uom.merge"
    _description = "Merges duplicate uoms"

    @api.model
    def default_get(self, default_fields):
        rec = super().default_get(default_fields)
        active_ids = self.env.context.get("active_ids", False)
        active_model = self.env.context.get("active_model", False)
        uoms = self.env[active_model].browse(active_ids)
        rec.update({"uom_ids": [(6, 0, uoms.ids)]})
        return rec

    dst_uom_id = fields.Many2one("uom.uom", string="Destination UOM")
    uom_ids = fields.Many2many(
        "uom.uom",
        "uom_rel",
        "uom_merge_id",
        "uom_id",
        string="UOMs to merge",
    )

    def action_merge(self):
        try:
            if len(self.uom_ids.category_id.ids) > 1:
                raise UserError(
                    _(
                        "You can not merge different category UOMs into one. "
                        "Please select UOMs from same category"
                    )
                )
            uoms_to_merge = self.uom_ids - self.dst_uom_id
            openupgrade_merge_records.merge_records(
                self.env,
                "uom.uom",
                uoms_to_merge.ids,
                self.dst_uom_id.id,
                field_spec={"factor": "other", "rounding": "other"},
                method="sql",
            )
        except Exception as e:
            _logger.warning(e)
            raise UserError(_("Error occur while merging uoms: %s") % e) from e
