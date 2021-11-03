# -*- coding: utf-8 -*-
# © 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, _


class ReceptionCheckpointWizard(models.TransientModel):
    _name = "reception.checkpoint.wizard"
    _description = "Select data for reception checkpoint"

    purchase_ids = fields.Many2many(
        comodel_name="purchase.order",
        # domain=lambda s: [("state" not in ("done", "cancel"))],
        string="Purchases",
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Vendors")
    date = fields.Date(
        default=fields.Date.today(),
        help="Select goods which should be received to this date",
    )

    @api.model
    def default_get(self, field_lists):
        res = super(ReceptionCheckpointWizard, self).default_get(field_lists)
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
                    res[afield] = old_obj[afield]
        return res

    @api.multi
    def button_select_moves(self):
        picking_types = self.env["stock.picking.type"].search(
            self._get_picking_type_domain()
        )
        if self.purchase_ids:
            moves = self._get_moves_from_purchases(self.purchase_ids, picking_types)
            name = ", ".join([x.name for x in self.purchase_ids])
        elif self.partner_id:
            purchases = self.env["purchase.order"].search(
                [
                    ("partner_id.commercial_partner_id", "=", self.partner_id.id),
                    (
                        "state",
                        "not in",
                        ("draft", "sent", "bid", "confirmed", "done", "cancel"),
                    ),
                ]
            )
            moves = self._get_moves_from_purchases(purchases, picking_types)
            name = self.partner_id.name
        return {
            "name": _("Reception checkpoint %s Date '%s'" % (name, self.date)),
            "res_model": "stock.move",
            "view_mode": "tree",
            "context": "{'date': '%s'}" % self.date,
            "domain": "[('id', 'in', %s)]" % moves.ids,
            # "auto_search": True,
            "view_id": self.env.ref(
                "stock_receive_checkpoint.reception_checkpoint_tree"
            ).id,
            "type": "ir.actions.act_window",
        }

    @api.model
    def _get_moves_from_purchases(self, purchases, picking_types):
        purch_line_ids = []
        for purch in purchases:
            purch_line_ids.extend(purch.order_line.ids)
        return self.env["stock.move"].search(
            [
                ("purchase_line_id", "in", purch_line_ids),
                ("picking_type_id", "in", picking_types.ids),
                ("state", "not in", ("done", "cancel")),
            ]
        )

    @api.model
    def _get_picking_type_domain(self):
        """ Inherit according to your own needs """
        return [("code", "=", "incoming")]

    @api.onchange("purchase_ids")
    def _purchase_onchange(self):
        if self.purchase_ids:
            self.partner_id = False

    @api.onchange("partner_id")
    def _partner_onchange(self):
        if self.partner_id:
            self.purchase_ids = False
