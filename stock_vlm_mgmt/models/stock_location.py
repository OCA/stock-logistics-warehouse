# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_vlm = fields.Boolean()
    vlm_vendor = fields.Selection(
        selection=[
            ("test", "Test"),
        ],
    )
    vlm_address = fields.Char(
        help=(
            "An VLM normally will be behind some propietary proxy that handles several "
            "VLMs at once, so we need to set which one corresponds to this location"
        )
    )
    vlm_hostname = fields.Char()
    vlm_port = fields.Char()
    vlm_removal_strategy = fields.Selection(
        selection=[
            ("fifo", "FIFO"),
            ("lifo", "LIFO"),
            ("optimal", "Less carrier movements"),
        ],
        default="fifo",
    )
    vlm_tray_ids = fields.One2many(
        comodel_name="stock.location.vlm.tray", inverse_name="location_id"
    )
    vlm_sequence_id = fields.Many2one(comodel_name="ir.sequence")
    vlm_user = fields.Char()
    vlm_password = fields.Char()

    def _prepare_vlm_request(self, **kw) -> dict:
        return {
            "task_type": kw.get("task_type", "release"),
            "task_id": self.vlm_sequence_id.next_by_id(),
            "address": self.vlm_address,
            "carrier": kw.get("carrier", "0"),
            "pos_x": kw.get("pos_x", "0"),
            "pos_y": kw.get("pos_y", "0"),
            "qty": str(kw.get("qty", "0")),
            "info1": kw.get("info1", "") or "",
            "info2": kw.get("info2", "") or "",
            "info3": kw.get("info3", "") or "",
            "info4": kw.get("info4", "") or "",
        }

    def send_vlm_request(self, data: dict, **options) -> dict:
        """Send request to the vendor methods. The vendor connector should deal with
        the connection issues transforming the response into these standard codes:
        -1: Connection refused
        -2: The request is issued but the response is lost
        -3: Timeout in the request
        -4: VLM Hardware issues
        """
        self.ensure_one()
        if not hasattr(self, "_%s_vlm_connector" % self.vlm_vendor):
            raise UserError(_("No implemented request connector for this vendor!"))
        timeout = (
            self.env["ir.config_parameter"].sudo().get_param("stock_vlm_mgmt.timeout")
        )
        vlm_connector = getattr(self, "_%s_vlm_connector" % self.vlm_vendor)()(
            self.vlm_hostname,
            self.vlm_port,
            timeout=timeout,
            user=self.vlm_user,
            password=self.vlm_password,
            **options
        )
        response = vlm_connector.request_operation(data)
        response_code = response.get("code", "")
        # These negative codes are issued by the connector and they're common connection
        # problems.
        if response_code == "-1":
            raise UserError(
                _("The connection was refused by the VLM and couldn't be stablished.")
            )
        elif response_code == "-2":
            raise UserError(
                _(
                    "The command response has been lost for unknown reasons. Did you "
                    "perform the operation on the VLM? Make sure there aren't "
                    "unconsistencies with the recorded data"
                )
            )
        elif response_code == "-3":
            raise UserError(
                _("The task couldn't be performed due to a timeout in the request"),
            )
        elif response_code == "-4":
            raise UserError(
                _(
                    "The task couldn't be performed. Try again or check  the vertical "
                    "lift module for hardware issues"
                )
            )
        elif response_code == "-5":
            raise UserError(_("The task was cancelled by the VLM"))
        return response

    def action_release_vlm_trays(self):
        """Send to the VLM a special command that releases all the trays"""
        data = self._prepare_vlm_request(
            task_type="release",
            info1=_(
                "%(user)s has requested a release of the trays from Odoo",
                user=self.env.user.name,
            ),
        )
        self.send_vlm_request(data)

    def action_view_vlm_tray(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_vlm_mgmt.location_vlm_tray_action"
        )
        action["domain"] = [("id", "in", self.vlm_tray_ids.ids)]
        action["context"] = dict(self.env.context, default_location_id=self.id)
        return action

    def action_view_vlm_quants(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_vlm_mgmt.location_quant_vlm_action"
        )
        action["domain"] = [("location_id", "=", self.id)]
        action["context"] = dict(
            self.env.context,
            vlm_inventory_mode=True,
        )
        view_id = self.env.ref("stock_vlm_mgmt.view_stock_quant_inventory_tree").id
        action.update(
            {
                "view_mode": "tree",
                "views": [
                    [view_id, "tree"] for view in action["views"] if view[1] == "tree"
                ],
            }
        )
        return action
