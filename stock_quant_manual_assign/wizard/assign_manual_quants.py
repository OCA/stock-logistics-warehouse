# Copyright 2015 Mikel Arregi - AvanzOSC
# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2018 Fanha Giang
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class AssignManualQuants(models.TransientModel):
    _name = "assign.manual.quants"
    _description = "Assign Manual Quants"

    @api.constrains("quants_lines")
    def _check_qty(self):
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for record in self.filtered("quants_lines"):
            if (
                float_compare(
                    record.lines_qty,
                    record.move_id.product_qty,
                    precision_digits=precision_digits,
                )
                > 0
            ):
                raise ValidationError(_("Quantity is higher than the needed one"))

    @api.depends("move_id", "quants_lines", "quants_lines.qty")
    def _compute_qties(self):
        for record in self:
            record.lines_qty = sum(
                record.quants_lines.filtered("selected").mapped("qty")
            )
            record.move_qty = record.move_id.product_qty - record.lines_qty

    lines_qty = fields.Float(
        string="Reserved qty",
        compute="_compute_qties",
        digits="Product Unit of Measure",
    )
    move_qty = fields.Float(
        string="Remaining qty",
        compute="_compute_qties",
        digits="Product Unit of Measure",
    )
    quants_lines = fields.One2many(
        "assign.manual.quants.lines", "assign_wizard", string="Quants"
    )
    move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Move",
    )

    def assign_quants(self):
        if self.move_qty < 0.0:
            raise ValidationError(_("Assigned more items than required"))
        move = self.move_id
        move._do_unreserve()
        for line in self.quants_lines:
            line._assign_quant_line()
        if move.picking_type_id.auto_fill_qty_done:
            # Auto-fill all lines as done
            for ml in move.move_line_ids:
                ml.qty_done = ml.product_qty
        move._recompute_state()
        move.mapped("picking_id")._compute_state()
        return {}

    @api.model
    def _domain_for_available_quants(self, move):
        return [
            ("location_id", "child_of", move.location_id.id),
            ("product_id", "=", move.product_id.id),
            ("quantity", ">", 0),
        ]

    @api.model
    def _get_available_quants(self, move):
        domain = self._domain_for_available_quants(move)
        return self.env["stock.quant"].search(domain)

    @api.model
    def default_get(self, fields):
        res = super(AssignManualQuants, self).default_get(fields)
        move = self.env["stock.move"].browse(self.env.context["active_id"])
        available_quants = self._get_available_quants(move)
        q_lines = []
        for quant in available_quants:
            line = self._prepare_wizard_line(move, quant)
            q_lines.append(line)
        res.update({"quants_lines": [(0, 0, x) for x in q_lines], "move_id": move.id})
        return res

    @api.model
    def _prepare_wizard_line(self, move, quant):
        line = {
            "quant_id": quant.id,
            "on_hand": quant.quantity,
            "location_id": quant.location_id.id,
            "lot_id": quant.lot_id.id,
            "package_id": quant.package_id.id,
            "owner_id": quant.owner_id.id,
            "selected": False,
        }
        move_lines = move.move_line_ids.filtered(
            lambda ml: (
                ml.location_id == quant.location_id
                and ml.lot_id == quant.lot_id
                and ml.owner_id == quant.owner_id
                and ml.package_id == quant.package_id
            )
        )
        line["qty"] = sum(move_lines.mapped("product_uom_qty"))
        line["selected"] = bool(line["qty"])
        line["reserved"] = quant.reserved_quantity - line["qty"]
        return line


class AssignManualQuantsLines(models.TransientModel):
    _name = "assign.manual.quants.lines"
    _description = "Assign Manual Quants Lines"
    _rec_name = "quant_id"
    _order = "location_id, lot_id, package_id"

    assign_wizard = fields.Many2one(
        comodel_name="assign.manual.quants",
        string="Move",
        required=True,
        ondelete="cascade",
    )
    quant_id = fields.Many2one(
        comodel_name="stock.quant",
        string="Quant",
        required=True,
        ondelete="cascade",
    )
    # Fields below are storable in order to be able to order by them. However,
    # there is a side effect: It is not possible to directly read the related
    # fields, e.g `self.lot_id`, because they are stored fields and have a group
    # restriction, so an access error would raise. To work around it, we should
    # access these fields from the quant: `self.quant_id.lot_id`.
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location",
        related="quant_id.location_id",
        groups="stock.group_stock_multi_locations",
        store=True,
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Lot",
        related="quant_id.lot_id",
        groups="stock.group_production_lot",
        store=True,
    )
    package_id = fields.Many2one(
        comodel_name="stock.quant.package",
        string="Package",
        related="quant_id.package_id",
        groups="stock.group_tracking_lot",
        store=True,
    )
    owner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Owner",
        related="quant_id.owner_id",
        groups="stock.group_tracking_owner",
        store=True,
    )
    # This is not correctly shown as related or computed, so we make it regular
    on_hand = fields.Float(
        string="On Hand",
        digits="Product Unit of Measure",
    )
    reserved = fields.Float(string="Others Reserved", digits="Product Unit of Measure")
    # If main field is set to readonly, they reset to 0.0 after a ValidationError
    # But they still need to be readonly so we solve it in this way
    on_hand_view = fields.Float(related="on_hand", readonly=True)
    reserved_view = fields.Float(related="reserved", readonly=True)
    selected = fields.Boolean(string="Select")
    hijack = fields.Boolean(string="Hijack")
    qty = fields.Float(string="QTY", digits="Product Unit of Measure")
    qty_had_hijack = fields.Boolean()

    @api.onchange("selected", "hijack")
    def _onchange_selected(self):
        for record in self:
            if not record.selected:
                record.qty = 0
                record.hijack = False
                record.qty_had_hijack = False
            elif not (record.qty and record.qty_had_hijack == record.hijack):
                # This takes current "snapshot" situation, so that we don't
                # have to compute each time if current reserved quantity is
                # for this current move. If other operations change available
                # quantity on quant, a constraint would be raised later on
                # validation.
                quant_qty = record.on_hand
                if not record.hijack:
                    # We ignore already reserved items, unless we're hijacking
                    quant_qty -= record.reserved
                record.qty = quant_qty
                record.qty_had_hijack = record.hijack

    @api.constrains("qty")
    def _check_qty(self):
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for record in self.filtered("qty"):
            quant = record.quant_id
            move_lines = record.assign_wizard.move_id.move_line_ids.filtered(
                lambda ml: (
                    ml.location_id == quant.location_id and ml.lot_id == quant.lot_id
                )
            )
            reserved = quant.reserved_quantity - sum(
                move_lines.mapped("product_uom_qty")
            )
            if record.hijack:
                # when hijacking, we disregard existing reservations
                reserved = 0
            if (
                float_compare(
                    record.qty,
                    record.quant_id.quantity - reserved,
                    precision_digits=precision_digits,
                )
                > 0
            ):
                raise ValidationError(
                    _(
                        "Selected line quantity is higher than the available "
                        "one. Maybe an operation with this product has been "
                        "done meanwhile or you have manually increased the "
                        "suggested value."
                    )
                )

    def _unreserve_other(self):
        self.ensure_one()
        # This function can only be used when hijacking
        assert self.hijack
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        reserved = self.quant_id.reserved_quantity
        move_lines = (
            self.env["stock.move.line"]
            .search(self.quant_id.action_view_stock_moves()["domain"])
            .filtered(lambda l: l.state == "assigned")
        )
        move_lines_total = sum(ml.product_uom_qty for ml in move_lines)
        if (
            float_compare(reserved, move_lines_total, precision_digits=precision_digits)
            == 0
        ):
            move_lines.unlink()
        else:
            raise ValidationError(
                _("Cannot hijack: found {} reserved ones but expected {}").format(
                    len(move_lines), reserved
                )
            )

    def _assign_quant_line(self):
        self.ensure_one()
        quant = self.env["stock.quant"]
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        move = self.assign_wizard.move_id
        if self.hijack:
            self._unreserve_other()
        if float_compare(self.qty, 0.0, precision_digits=precision_digits) > 0:
            available_quantity = quant._get_available_quantity(
                move.product_id,
                self.quant_id.location_id,
                lot_id=self.quant_id.lot_id,
                package_id=self.quant_id.package_id,
                owner_id=self.quant_id.owner_id,
            )
            if (
                float_compare(
                    available_quantity, 0.0, precision_digits=precision_digits
                )
                <= 0
            ):
                return
            move._update_reserved_quantity(
                self.qty,
                available_quantity,
                self.quant_id.location_id,
                lot_id=self.quant_id.lot_id,
                package_id=self.quant_id.package_id,
                owner_id=self.quant_id.owner_id,
                strict=True,
            )
