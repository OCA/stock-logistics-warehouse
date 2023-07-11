# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models


class SaleStockReserve(models.TransientModel):
    _name = "sale.stock.reserve"
    _description = "Sale Stock Reserve"

    @api.model
    def _default_location_id(self):
        return self.env["stock.reservation"].get_location_from_ref(
            "stock.stock_location_stock"
        )

    @api.model
    def _default_location_dest_id(self):
        return self.env["stock.reservation"]._default_location_dest_id()

    def _default_owner(self):
        """If sale_owner_stock_sourcing is installed, it adds an owner field
        on sale order lines. Use it.

        """
        model = self.env[self.env.context["active_model"]]
        if model._name == "sale.order":
            lines = model.browse(self.env.context["active_id"]).order_line
        else:
            lines = model.browse(self.env.context["active_ids"])

        try:
            owners = {line.stock_owner_id for line in lines}
        except AttributeError:
            return self.env["res.partner"]
            # module sale_owner_stock_sourcing not installed, fine

        if len(owners) == 1:
            return owners.pop()
        elif len(owners) > 1:
            raise exceptions.Warning(
                _(
                    """The lines have different owners. Please reserve them
                    individually with the reserve button on each one."""
                )
            )

        return self.env["res.partner"]

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
    owner_id = fields.Many2one("res.partner", "Stock Owner", default=_default_owner)

    def _prepare_stock_reservation(self, line):
        self.ensure_one()

        picking_env = self.env["stock.picking"]
        reservation_env = self.env["stock.reservation"]
        picking_type_id = reservation_env.with_context(
            warehouse_id=line.order_id.warehouse_id.id
        )._default_picking_type_id()
        location_id = (self.location_id.id,)
        if picking_type_id and not location_id:
            picking = self.env["stock.picking"].new(
                {"picking_type_id": picking_type_id}
            )
            picking.onchange_picking_type()
            location_id = picking.location_id.id
        location_dest_id = (
            self.location_dest_id.id or reservation_env._default_location_dest_id()
        )
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
            "name": "{} ({})".format(line.order_id.name, line.name),
            "location_id": self.location_id.id,
            "location_dest_id": self.location_dest_id.id,
            "note": self.note,
            "price_unit": line.price_unit,
            "sale_line_id": line.id,
            "restrict_partner_id": self.owner_id.id,
            "picking_id": picking_id.id,
        }

    def stock_reserve(self, line_ids):
        self.ensure_one()

        lines = self.env["sale.order.line"].browse(line_ids)
        for line in lines:
            if not line.is_stock_reservable:
                continue
            vals = self._prepare_stock_reservation(line)
            reserv = self.env["stock.reservation"].create(vals)
            reserv.reserve()
        return True

    def button_reserve(self):
        env = self.env
        self.ensure_one()
        close = {"type": "ir.actions.act_window_close"}
        active_model = env.context.get("active_model")
        active_ids = env.context.get("active_ids")
        if not (active_model and active_ids):
            return close

        if active_model == "sale.order":
            sales = env["sale.order"].browse(active_ids)
            line_ids = [line.id for sale in sales for line in sale.order_line]

        if active_model == "sale.order.line":
            line_ids = active_ids

        self.stock_reserve(line_ids)
        return close
