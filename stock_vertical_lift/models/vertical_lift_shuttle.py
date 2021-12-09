# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import socket
import ssl

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


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
    server = fields.Char(help="hostname or IP address of the server")
    port = fields.Integer(
        help="network port of the server on which to send the message"
    )
    use_tls = fields.Boolean(
        help="set this if the server expects TLS wrapped communication"
    )
    command_ids = fields.One2many(
        "vertical.lift.command", "shuttle_id", string="Hardware commands"
    )
    _sql_constraints = [
        (
            "location_id_unique",
            "UNIQUE(location_id)",
            "You cannot have two shuttles using the same location.",
        )
    ]

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
            "pick": ("stock_vertical_lift." "vertical_lift_operation_pick_screen_view"),
            "put": ("stock_vertical_lift." "vertical_lift_operation_put_screen_view"),
            "inventory": (
                "stock_vertical_lift." "vertical_lift_operation_inventory_screen_view"
            ),
        }

    def _hardware_send_message(self, payload):
        """default implementation for message sending

        If in hardware is 'simulation' then display a simple message.
        Otherwise defaults to connecting to server:port using a TCP socket
        (optionnally wrapped with TLS) and sending the payload.

        :param payload: a bytes object containing the payload

        """
        self.ensure_one()
        _logger.info("send %r", payload)
        command_values = {"shuttle_id": self.id, "command": payload.decode()}

        self.env["vertical.lift.command"].sudo().create(command_values)
        if self.hardware == "simulation":
            self.env.user.notify_info(message=payload, title=_("Lift Simulation"))
            return True
        else:
            conn = self._hardware_get_server_connection()
            try:
                offset = 0
                while True:
                    size = conn.send(payload[offset:])
                    offset += size
                    if offset >= len(payload) or not size:
                        break
            finally:
                self._hardware_release_server_connection(conn)

    def _hardware_response_callback(self, command):
        """should be called when a response is received from the hardware

        :param response: a string
        """
        success = self._check_server_response(command)
        self._send_notification_refresh(success)

    def _check_server_response(self, command):
        """Use this to check if the response is a success or a failure

        :param payload: the payload sent
        :param response: the response received
        :return: True if the response is a succes, False otherwise
        """
        return True

    def _hardware_release_server_connection(self, conn):
        conn.close()

    def _hardware_get_server_connection(self):
        """This implementation will yield a new connection to the server
        and close() it when exiting the context.
        Override to match the communication protocol of your hardware"""
        conn = socket.create_connection((self.server, self.port))
        if self.use_tls:
            ctx = ssl.create_default_context()
            self._hardware_update_tls_context(ctx)
            conntls = ctx.wrap_socket(conn, server_hostname=self.server)
            return conntls
        else:
            return conn

    def _hardware_update_tls_context(self, context):
        """Update the TLS context, e.g. to add a client certificate.

        This method does nothing, override to match your communication
        protocol."""
        pass  # noqa

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
                "withControlPanel": False,
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

    def action_back_to_settings(self):
        self.release_vertical_lift_tray()
        action_xmlid = "stock_vertical_lift.vertical_lift_shuttle_action"
        action = self.env["ir.actions.act_window"]._for_xml_id(action_xmlid)
        action["target"] = "main"
        return action

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
        self.release_vertical_lift_tray()
        return self.action_open_screen()

    def switch_put(self):
        self.mode = "put"
        self.release_vertical_lift_tray()
        return self.action_open_screen()

    def switch_inventory(self):
        self.mode = "inventory"
        self.release_vertical_lift_tray()
        return self.action_open_screen()

    def _hardware_vertical_lift_release_tray_payload(self):
        """Prepare "release" message to be sent to the vertical lift hardware

        Private method, this is where the implementation actually happens.
        Addons can add their instructions based on the hardware used for
        this location.

        The hardware used for a location can be found in:

        ``self.hardware``

        Each addon can implement its own mechanism depending of this value
        and must call ``super``.

        The method must send the command to the vertical lift to release (close)
        the tray.

        Returns a message in bytes, that will be sent through
        ``VerticalLiftShuttle._hardware_send_message()``.
        """
        if self.hardware == "simulation":
            message = _("Releasing tray")
            return message.encode("utf-8")
        else:
            raise NotImplementedError()

    def release_vertical_lift_tray(self):
        """Send instructions to the vertical lift hardware to close trays

        The actual implementation of the method goes in the private method
        ``_hardware_vertical_lift_release_tray()``.
        """
        self.ensure_one()
        payload = self._hardware_vertical_lift_release_tray_payload()
        return self._hardware_send_message(payload)

    def _send_notification_refresh(self, success):
        """Send a refresh notification to the current opened screen

        The form controller on the front-end side will instantaneously
        refresh the form with the latest committed data.

        It can be used for instance after a vertical lift hardware
        event occurred to inform the user on their screen.

        The method is private only to prevent xml/rpc calls to
        interact with the screen.
        """
        # XXX do we want to do something special in the notification?
        self._operation_for_mode()._send_notification_refresh()
