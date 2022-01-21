# Copyright 2017 Creu Blanca
# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class WizardStockRequestOrderKanban(models.TransientModel):
    _name = "wizard.stock.request.order.kanban"
    _description = "Stock Request Order Kanban Wizard"
    _inherit = "wizard.stock.request.kanban"

    order_id = fields.Many2one("stock.request.order", required=True)

    def validate_kanban(self, barcode):
        res = super().validate_kanban(barcode)
        if self.order_id.stock_request_ids.filtered(
            lambda r: r.kanban_id == self.kanban_id
        ):
            self.status = _("Barcode %s is on the order") % barcode
            self.status_state = 1
            return False
        if self.order_id.state != "draft":
            raise ValidationError(
                _("Lines only can be added on orders with draft state")
            )
        if not self.order_id.company_id:
            self.order_id.company_id = self.kanban_id.company_id
        elif self.order_id.company_id != self.kanban_id.company_id:
            raise ValidationError(_("Company must be the same"))
        if (
            self.kanban_id.procurement_group_id
            and self.order_id.procurement_group_id
            != self.kanban_id.procurement_group_id
        ):
            raise ValidationError(_("Procurement group must be the same"))
        if self.order_id.location_id != self.kanban_id.location_id:
            raise ValidationError(_("Location must be the same"))
        if self.order_id.warehouse_id != self.kanban_id.warehouse_id:
            raise ValidationError(_("Warehouse must be the same"))
        return res

    def stock_request_kanban_values(self):
        res = super().stock_request_kanban_values()
        res["order_id"] = (self.order_id.id,)
        res["expected_date"] = fields.Datetime.to_string(self.order_id.expected_date)
        return res

    def stock_request_ending(self):
        return

    def barcode_ending(self):
        res = super().barcode_ending()
        self.order_id = self.stock_request_id.order_id
        return res
