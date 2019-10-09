# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class VerticalLiftShuttle(models.Model):
    _name = "vertical.lift.shuttle"
    _inherit = "barcodes.barcode_events_mixin"
    _description = "Vertical Lift Shuttle"

    name = fields.Char()
    mode = fields.Selection(
        [("pick", "Pick"), ("put", "Put"), ("inventory", "Inventory")],
        default="pick",
        required=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        required=True,
        domain="[('vertical_lift_kind', '=', 'shuttle')]",
        ondelete="restrict",
        help="The Shuttle source location for Pick operations "
        "and destination location for Put operations.",
    )
    hardware = fields.Selection(
        selection="_selection_hardware", default="simulation", required=True
    )

    _sql_constraints = [
        (
            "location_id_unique",
            "UNIQUE(location_id)",
            "You cannot have two shuttles using the same location.",
        )
    ]

    @api.model
    def _selection_hardware(self):
        return [("simulation", "Simulation")]

    @property
    def _model_for_mode(self):
        return {
            "pick": "vertical.lift.operation.pick",
            "put": "vertical.lift.operation.put",
            "inventory": "vertical.lift.operation.inventory",
        }

    @property
    def _screen_view_for_mode(self):
        return {
            "pick": (
                "stock_vertical_lift."
                "vertical_lift_operation_pick_screen_view"
            ),
            "put": (
                "stock_vertical_lift."
                "vertical_lift_operation_put_screen_view"
            ),
            "inventory": (
                "stock_vertical_lift."
                "vertical_lift_operation_inventory_screen_view"
            ),
        }

    def _operation_for_mode(self):
        model = self._model_for_mode[self.mode]
        record = self.env[model].search([("shuttle_id", "=", self.id)])
        if not record:
            record = self.env[model].create({"shuttle_id": self.id})
        return record

    def action_open_screen(self):
        self.ensure_one()
        assert self.mode in ("pick", "put", "inventory")
        screen_xmlid = self._screen_view_for_mode[self.mode]
        operation = self._operation_for_mode()
        operation.on_screen_open()
        return {
            "type": "ir.actions.act_window",
            "res_model": operation._name,
            "views": [[self.env.ref(screen_xmlid).id, "form"]],
            "res_id": operation.id,
            "target": "fullscreen",
            "flags": {
                "headless": True,
                "form_view_initial_mode": "edit",
                "no_breadcrumbs": True,
            },
        }

    def action_menu(self):
        menu_xmlid = "stock_vertical_lift.vertical_lift_shuttle_form_menu"
        return {
            "type": "ir.actions.act_window",
            "res_model": "vertical.lift.shuttle",
            "views": [[self.env.ref(menu_xmlid).id, "form"]],
            "name": _("Menu"),
            "target": "new",
            "res_id": self.id,
        }

    def action_manual_barcode(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "vertical.lift.shuttle.manual.barcode",
            "view_mode": "form",
            "name": _("Barcode"),
            "target": "new",
        }

    # TODO: should the mode be changed on all the shuttles at the same time?
    def switch_pick(self):
        self.mode = "pick"
        return self.action_open_screen()

    def switch_put(self):
        self.mode = "put"
        return self.action_open_screen()

    def switch_inventory(self):
        self.mode = "inventory"
        return self.action_open_screen()


class VerticalLiftShuttleManualBarcode(models.TransientModel):
    _name = "vertical.lift.shuttle.manual.barcode"
    _description = "Action to input a barcode"

    barcode = fields.Char(string="Barcode")

    @api.multi
    def button_save(self):
        active_id = self.env.context.get("active_id")
        model = self.env.context.get("active_model")
        record = self.env[model].browse(active_id).exists()
        if not record:
            return
        if self.barcode:
            record.on_barcode_scanned(self.barcode)
