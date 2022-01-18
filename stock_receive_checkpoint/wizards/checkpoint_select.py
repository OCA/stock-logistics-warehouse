# -*- coding: utf-8 -*-
# © 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DT


class ReceptionCheckpointSelectionWizard(models.TransientModel):
    _name = "reception.checkpoint.selection.wizard"
    _description = "Select data for reception checkpoint"

    purchase_ids = fields.Many2many(
        comodel_name="purchase.order",
        # domain=lambda s: [("state" not in ("done", "cancel"))],
        string="Purchases",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        domain=[("supplier", "=", True)],
    )
    date = fields.Date(
        help="Select goods which should be received to this date or "
        "have been received to this date",
    )
    today = fields.Boolean(help="Check to apply today's date")
    include_received = fields.Boolean()

    @api.model
    def default_get(self, field_lists):
        res = super(ReceptionCheckpointSelectionWizard, self).default_get(field_lists)
        old_obj = self.search(
            [("write_uid", "=", self.env.user.id)], limit=1, order="write_date DESC"
        )
        if old_obj:
            for afield in field_lists:
                if old_obj._fields[afield].type == "many2many":
                    res[afield] = [(6, 0, old_obj[afield].ids)]
                elif old_obj._fields[afield].type == "many2one":
                    res[afield] = old_obj[afield].id
                else:
                    if afield not in ("today"):
                        res[afield] = old_obj[afield]
        return res

    @api.onchange("today")
    def onchange_today(self):
        if self.today:
            self.date = fields.Date.today()

    @api.multi
    def ui_select_moves(self):
        purchases, name = self._get_purchases()
        moves = self._get_moves(purchases)
        date = datetime.strptime(self.date, DT).strftime("%d/%m/%Y")
        line_ids = (
            self.env["reception.checkpoint"]
            .with_context(checkpoint_date=date)
            ._create_checkpoint_moves(moves)
        )
        return {
            "name": _("%s %s Reception Checkpoint" % (name, date)),
            "res_model": "reception.checkpoint",
            "view_mode": "tree",
            "context": "{'checkpoint_date': '%s'}" % self.date,
            "domain": "[('id', 'in', %s)]" % line_ids,
            "view_id": self.env.ref(
                "stock_receive_checkpoint.reception_checkpoint_tree_view"
            ).id,
            "type": "ir.actions.act_window",
        }

    def _get_purchases(self):
        self.ensure_one()
        if not self.date:
            self.date = fields.Date.today()
        if self.purchase_ids:
            name = ", ".join([x.name for x in self.purchase_ids])
            purchases = self.purchase_ids
        elif self.partner_id:
            purchases = self.env["purchase.order"].search(
                [
                    (
                        "partner_id.commercial_partner_id",
                        "=",
                        self.partner_id.commercial_partner_id.id,
                    ),
                    (
                        "state",
                        "not in",
                        ("draft", "sent", "bid", "confirmed", "done", "cancel"),
                    ),
                ]
            )
            name = self.partner_id.name
            if not purchases:
                raise UserError(_("No purchase data for this vendor"))
        else:
            raise UserError(_("You must specify vendor or purchases"))
        return (purchases, name)

    @api.model
    def _get_moves(self, purchases):
        purch_line_ids, picking_ids, picking_types = [], [], []
        if self._get_picking_type_domain():
            picking_types = self.env["stock.picking.type"].search(
                self._get_picking_type_domain()
            )
        for purch in purchases:
            purch_line_ids.extend(purch.order_line.ids)
            picking_ids.extend(purch.picking_ids.ids)
        excluded_states = ["cancel", "done"]
        if self.include_received:
            excluded_states = ["cancel"]
        domain = self._get_moves_domain(picking_ids, excluded_states, picking_types)
        moves = self.env["stock.move"].search(domain)
        if not moves:
            str_domain = str(domain).replace("'|'", "\n'|'").replace("'&'", "\n'&'")
            raise UserError(
                "%s\n\n%s"
                % (
                    _("No stock moves for these purchases %s")
                    % [x.name for x in purchases],
                    str_domain,
                )
            )
        return moves

    @api.model
    def _get_picking_type_domain(self):
        """Inherit according to your own needs
        Basics case only need pickings attached to purchases
        """
        return None

    @api.model
    def _get_moves_domain(self, picking_ids, excluded_states, picking_types):
        """Inherit according to your own needs"""
        domain = []
        if picking_types:
            domain.append(
                ("picking_type_id", "in", picking_types.ids),
            )
        domain.extend(
            [
                ("picking_id", "in", picking_ids),
                "|",
                "&",
                ("date", "<=", self.date),
                ("state", "=", "done"),
                "&",
                "&",
                ("date_expected", ">=", self.date),
                ("date_expected", "<=", self.date),
                ("state", "not in", excluded_states),
            ]
        )
        return domain

    @api.onchange("purchase_ids")
    def _purchase_onchange(self):
        if self.purchase_ids:
            self.partner_id = False

    @api.onchange("partner_id")
    def _partner_onchange(self):
        if self.partner_id:
            self.purchase_ids = False
