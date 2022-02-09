# Copyright 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MakeProcurementOrderpoint(models.TransientModel):
    _name = "make.procurement.orderpoint"
    _description = "Make Procurements from Orderpoints"

    item_ids = fields.One2many(
        "make.procurement.orderpoint.item", "wiz_id", string="Items"
    )

    @api.model
    def _prepare_item(self, orderpoint):
        return {
            "qty": orderpoint.procure_recommended_qty,
            "qty_without_security": orderpoint.procure_recommended_qty,
            "uom_id": orderpoint.product_uom.id,
            "date_planned": orderpoint.procure_recommended_date,  # string
            "orderpoint_id": orderpoint.id,
            "product_id": orderpoint.product_id.id,
            "warehouse_id": orderpoint.warehouse_id.id,
            "location_id": orderpoint.location_id.id,
        }

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        if not self.user_has_groups(
            "stock_orderpoint_manual_procurement.group_change_orderpoint_procure_qty"
        ):  # noqa
            # Redirect to readonly qty form view
            view_id = self.env.ref(
                "stock_orderpoint_manual_procurement.view_make_procure_without_security"
            ).id  # noqa
        return super(MakeProcurementOrderpoint, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )

    @api.model
    def default_get(self, fields):
        res = super(MakeProcurementOrderpoint, self).default_get(fields)
        orderpoint_obj = self.env["stock.warehouse.orderpoint"]
        orderpoint_ids = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]

        if not orderpoint_ids:
            return res
        assert active_model == "stock.warehouse.orderpoint", "Bad context propagation"

        items = []
        for line in orderpoint_obj.browse(orderpoint_ids):
            items.append([0, 0, self._prepare_item(line)])
        res["item_ids"] = items
        return res

    def make_procurement(self):
        self.ensure_one()
        errors = []
        # User requesting the procurement is passed by context to be able to
        # update final MO, PO or trasfer with that information.
        pg_obj = self.env["procurement.group"].with_context(requested_uid=self.env.user)
        procurements = []
        for item in self.item_ids:
            if not item.qty:
                raise ValidationError(_("Quantity must be positive."))
            if not item.orderpoint_id:
                raise ValidationError(_("No reordering rule found!"))
            values = item.orderpoint_id._prepare_procurement_values()
            values["date_planned"] = fields.Datetime.to_string(
                fields.Date.from_string(item.date_planned)
            )
            procurements.append(
                pg_obj.Procurement(
                    item.orderpoint_id.product_id,
                    item.qty,
                    item.uom_id,
                    item.orderpoint_id.location_id,
                    item.orderpoint_id.name,
                    item.orderpoint_id.name,
                    item.orderpoint_id.company_id,
                    values,
                )
            )
        try:
            # Run procurement
            pg_obj.run(procurements)
        except UserError as error:
            errors.append(error.name)
        if errors:
            raise UserError("\n".join(errors))
        return {"type": "ir.actions.act_window_close"}


class MakeProcurementOrderpointItem(models.TransientModel):
    _name = "make.procurement.orderpoint.item"
    _description = "Make Procurements from Orderpoint Item"

    wiz_id = fields.Many2one(
        "make.procurement.orderpoint",
        string="Wizard",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    qty = fields.Float(string="Qty")
    qty_without_security = fields.Float(string="Quantity")
    uom_id = fields.Many2one(string="Unit of Measure", comodel_name="uom.uom")
    date_planned = fields.Date(string="Planned Date", required=False)
    orderpoint_id = fields.Many2one(
        string="Reordering rule",
        comodel_name="stock.warehouse.orderpoint",
        readonly=False,
    )
    product_id = fields.Many2one(
        string="Product", comodel_name="product.product", readonly=True
    )
    warehouse_id = fields.Many2one(
        string="Warehouse", comodel_name="stock.warehouse", readonly=True
    )
    location_id = fields.Many2one(
        string="Location", comodel_name="stock.location", readonly=True
    )

    @api.onchange("uom_id")
    def onchange_uom_id(self):
        for rec in self:
            rec.qty = rec.orderpoint_id.product_uom._compute_quantity(
                rec.orderpoint_id.procure_recommended_qty, rec.uom_id
            )
