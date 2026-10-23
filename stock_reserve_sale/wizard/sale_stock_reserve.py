# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class SaleStockReserve(models.TransientModel):
    _name = "sale.stock.reserve"
    _description = "Sale Stock Reserve"

    @api.model
    def _default_location_id(self):
        domain = [
            "|",
            ("company_id", "=", self.env.company.id),
            ("company_id", "=", False),
        ]
        return self.env["stock.warehouse"].search(domain, limit=1).lot_stock_id

    @api.model
    def _default_location_dest_id(self):
        return self.env["stock.reservation"]._default_location_dest_id()

    location_id = fields.Many2one(
        "stock.location", "Source Location", required=True, default=_default_location_id
    )
    location_dest_id = fields.Many2one(
        "stock.location",
        "Reservation Location",
        required=True,
        help="Location where the system will reserve the " "products.",
        default=_default_location_dest_id,
    )
    date_validity = fields.Date(
        "Validity Date",
        help="If a date is given, the reservations will be released "
        "at the end of the validity.",
    )
    note = fields.Text("Notes")
    owner_id = fields.Many2one("res.partner", "Stock Owner")
    line_ids = fields.One2many(
        "sale.stock.reserve.line", "wizard_id", string="Lines to Reserve"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "line_ids" in fields_list:
            res["line_ids"] = [
                Command.create({"sale_line_id": line.id})
                for line in self._get_sale_order_lines()
            ]
        return res

    @api.model
    def _get_sale_order_lines(self):
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids") or []
        lines = self.env["sale.order.line"]
        if active_model == "sale.order":
            lines = self.env["sale.order"].browse(active_ids).order_line
        elif active_model == "sale.order.line":
            lines = lines.browse(active_ids)
        return lines.filtered("is_stock_reservable")

    def _prepare_stock_reservation(self, line):
        self.ensure_one()

        picking_env = self.env["stock.picking"]
        reservation_env = self.env["stock.reservation"]
        picking_type_id = reservation_env._get_picking_type(
            self.location_id, line.order_id.company_id.id
        ).id
        location_id = self.location_id.id
        if picking_type_id and not location_id:
            picking = self.env["stock.picking"].new(
                {"picking_type_id": picking_type_id}
            )
            picking._onchange_picking_type()
            location_id = picking.location_id.id
        location_dest_id = (
            self.location_dest_id.id or reservation_env._default_location_dest_id()
        )
        picking_id = picking_env
        if line.order_id.company_id.sale_stock_reservation_picking:
            picking_id = picking_env.search(
                [
                    ("sale_reserve_id", "=", line.order_id.id),
                    ("location_id", "=", location_id),
                    ("location_dest_id", "=", location_dest_id),
                    ("state", "not in", ["cancel", "done"]),
                ],
                limit=1,
            )
            if not picking_id:
                picking_id = picking_env.create(
                    {
                        "location_id": location_id,
                        "location_dest_id": location_dest_id,
                        "origin": line.order_id.name,
                        "sale_reserve_id": line.order_id.id,
                        "picking_type_id": picking_type_id,
                        "company_id": line.order_id.company_id.id,
                    }
                )
        return {
            "product_id": line.product_id.id,
            "product_uom": line.product_uom.id,
            "product_uom_qty": line.product_uom_qty,
            "date_validity": self.date_validity,
            "name": f"{line.order_id.name} ({line.name})",
            "location_id": self.location_id.id,
            "location_dest_id": self.location_dest_id.id,
            "note": self.note,
            "price_unit": line.price_unit,
            "sale_line_id": line.id,
            "restrict_partner_id": self.owner_id.id,
            "picking_id": picking_id.id,
            "picking_type_id": picking_type_id,
        }

    def _prepare_stock_reservation_vals_list(self, reserve_line):
        self.ensure_one()
        vals = self._prepare_stock_reservation(reserve_line.sale_line_id)
        vals["product_uom_qty"] = reserve_line.quantity
        return [vals]

    def button_reserve(self):
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda line: line.sale_line_id.is_stock_reservable
            and not float_is_zero(
                line.quantity, precision_rounding=line.product_uom.rounding
            )
        )
        if not lines:
            raise UserError(
                _(
                    "There is nothing to reserve. Set a quantity to reserve "
                    "on at least one line."
                )
            )
        for line in lines:
            reservations = self.env["stock.reservation"].create(
                self._prepare_stock_reservation_vals_list(line)
            )
            reservations.reserve()
