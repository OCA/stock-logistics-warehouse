# Copyright (C) 2022 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StocklocationContentCheck(models.Model):
    _name = "stock.location.content.check"
    _description = "Stock Location Content Check"

    name = fields.Char(string="Name", required=True, default="Draft")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("completed", "Completed"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        default="draft",
    )
    date = fields.Datetime(string="Date", required=True)
    location_id = fields.Many2one("stock.location", string="Location", required=True)
    user_id = fields.Many2one(
        "res.users", string="User", required=True, default=lambda self: self.env.user
    )
    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company.id
    )
    line_ids = fields.One2many(
        "stock.location.content.check.line", "check_id", string="Products"
    )
    picking_ids = fields.One2many("stock.picking", "check_id", string="Pickings")

    @api.model
    def create(self, vals):
        vals.update(
            {
                "name": self.env["ir.sequence"].next_by_code(
                    "stock.location.content.check"
                )
            }
        )
        return super(StocklocationContentCheck, self).create(vals)

    def action_confirm(self):
        for rec in self:
            rec.state = "confirmed"

    def action_complete(self):
        for rec in self:
            rec._create_out_pick()
            rec._create_internal_pick()
            rec.state = "completed"

    def _create_out_pick(self):
        picking_obj = self.env["stock.picking"]
        location_id = self.location_id
        location_dest_id = self.env["stock.location"].search(
            [("usage", "=", "customer")], limit=1
        )
        wh_id = location_id.get_warehouse()
        pick_type_id = wh_id.out_type_id
        for rec in self:
            move_lines = []
            for line in rec.line_ids:
                if line.current_qty >= (line.current_qty - line.counted_qty) > 0:
                    move_lines.append(
                        (
                            0,
                            0,
                            {
                                "name": line.product_id.name,
                                "product_id": line.product_id.id,
                                "product_uom": line.product_id.uom_id.id,
                                "product_uom_qty": line.current_qty - line.counted_qty,
                                "picking_type_id": pick_type_id.id,
                                "location_id": location_id.id,
                                "location_dest_id": location_dest_id.id,
                            },
                        )
                    )
            if move_lines:
                picking_obj.create(
                    {
                        "picking_type_id": pick_type_id.id,
                        "location_id": location_id.id,
                        "location_dest_id": location_dest_id.id,
                        "move_lines": move_lines,
                        "check_id": rec.id,
                    }
                )

    def _create_internal_pick(self):
        picking_obj = self.env["stock.picking"]
        for rec in self:
            move_lines_self_parent = []
            move_lines_parent_self = []
            if rec.location_id.location_id.usage == "view":
                raise UserError(_("You can't use view type location in transfer."))
            wh_id = rec.location_id.get_warehouse()
            pick_type_id = wh_id.int_type_id
            for line in rec.line_ids:
                if not line.replenished_qty == 0.0:
                    if line.replenished_qty > 0.0:
                        location_id_ps = rec.location_id.location_id.id
                        location_dest_id_ps = rec.location_id.id
                        product_qty_ps = line.replenished_qty
                        move_lines_parent_self.append(
                            (
                                0,
                                0,
                                {
                                    "name": line.product_id.name,
                                    "product_id": line.product_id.id,
                                    "product_uom": line.product_id.uom_id.id,
                                    "product_uom_qty": product_qty_ps,
                                    "picking_type_id": pick_type_id.id,
                                    "location_id": location_id_ps,
                                    "location_dest_id": location_dest_id_ps,
                                },
                            )
                        )
                    if line.replenished_qty < 0.0:
                        location_id_sp = rec.location_id.id
                        location_dest_id_sp = rec.location_id.location_id.id
                        product_qty_sp = abs(line.replenished_qty)
                        move_lines_self_parent.append(
                            (
                                0,
                                0,
                                {
                                    "name": line.product_id.name,
                                    "product_id": line.product_id.id,
                                    "product_uom": line.product_id.uom_id.id,
                                    "product_uom_qty": product_qty_sp,
                                    "picking_type_id": pick_type_id.id,
                                    "location_id": location_id_sp,
                                    "location_dest_id": location_dest_id_sp,
                                },
                            )
                        )

            if move_lines_parent_self:
                picking_obj.create(
                    {
                        "picking_type_id": pick_type_id.id,
                        "location_id": location_id_ps,
                        "location_dest_id": location_dest_id_ps,
                        "move_lines": move_lines_parent_self,
                        "check_id": rec.id,
                    }
                )
            if move_lines_self_parent:
                picking_obj.create(
                    {
                        "picking_type_id": pick_type_id.id,
                        "location_id": location_id_sp,
                        "location_dest_id": location_dest_id_sp,
                        "move_lines": move_lines_self_parent,
                        "check_id": rec.id,
                    }
                )

    def action_cancel(self):
        for rec in self:
            rec._cancel_all_pickings()
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            rec._cancel_all_pickings()
            rec.state = "draft"

    def _cancel_all_pickings(self):
        for rec in self:
            for pick in rec.picking_ids:
                pick.action_cancel()

    def action_close(self):
        for rec in self:
            for picking in rec.picking_ids.filtered(
                lambda a: a.state not in ("done", "cancel")
            ):
                picking.action_confirm()
                picking.action_assign()
                for movel in picking.move_lines:
                    movel.quantity_done = movel.product_uom_qty
                picking.button_validate()
            rec.state = "closed"

    @api.onchange("location_id")
    def _onchange_location_id(self):
        check_lines = []
        for rec in self:
            product_lines = (
                rec.location_id.template_id
                and rec.location_id.template_id.line_ids.filtered(
                    lambda x: x.in_checkout
                )
            )
            for line in product_lines:
                check_lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "check_id": rec.id,
                        },
                    )
                )
            rec.write({"line_ids": [(6, 0, [])]})
            rec.write({"line_ids": check_lines})
            rec.line_ids._onchange_replenished_qty()

    def action_view_delivery_order(self):
        self.ensure_one()
        return {
            "name": _("Delivery Order"),
            "res_model": "stock.picking",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "domain": [
                ("check_id", "=", self.id),
                ("picking_type_code", "=", "outgoing"),
            ],
        }

    def action_view_transfer(self):
        self.ensure_one()
        return {
            "name": _("Internal Transfer"),
            "res_model": "stock.picking",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "domain": [
                ("check_id", "=", self.id),
                ("picking_type_code", "=", "internal"),
            ],
        }
