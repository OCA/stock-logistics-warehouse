# -*- coding: utf-8 -*-
# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from collections import defaultdict

from openerp import models, api, fields, _

# from openerp.exceptions import Warning as UserError

# from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DT


class ReceptionCheckpoint(models.TransientModel):
    _name = "reception.checkpoint"
    _description = "Reception checkpoint"

    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    partner_ref = fields.Char(compute="_compute_partner_ref")
    date_planned = fields.Date(related="purchase_line_id.date_planned")
    purch_line = fields.Integer()
    purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line", string="Order Line"
    )
    order_id = fields.Many2one(
        comodel_name="purchase.order", related="purchase_line_id.order_id"
    )
    origin = fields.Char(related="purchase_line_id.order_id.origin")
    ordered_qty = fields.Float()
    received_date = fields.Date(string="Last received")
    diff_qty = fields.Float()
    received_qty = fields.Float()
    timing = fields.Char(help="Technical field to apply color in tree view")

    @api.depends("product_id")
    def _compute_partner_ref(self):
        def get_ref(name):
            if name[:1] == "[":
                pos = name.find("]")
                if pos:
                    return name[1:pos]

        vendor = self.env.context.get("vendor")
        for rec in self:
            if rec.product_id and vendor:
                ref_vdr = rec.product_id.with_context(partner_id=vendor).name_get()
                if ref_vdr:
                    rec.partner_ref = get_ref(ref_vdr[0][1])

    @api.model
    def _create_checkpoint_moves(self, moves):
        def init_dict(mfield, ttype):
            if mfield not in pline:
                if ttype == int:
                    pline[mfield] = 0
                elif ttype == "date":
                    pline[mfield] = False

        lines = defaultdict(dict)
        line_ids = []
        uid = self.env.user.id
        for move in moves:
            pline = lines[move.purchase_line_id]
            pline.update(
                {
                    "product_id": move.product_id.id,
                    "purchase_line_id": move.purchase_line_id.id,
                    "purch_line": move.purchase_line_id
                    and move.purchase_line_id.id
                    or False,
                    "ordered_qty": move.purchase_line_id.product_qty,
                    "order_id": move.purchase_line_id.order_id.id,
                    "write_uid": uid,
                }
            )
            init_dict("received_qty", int)
            if move.state == "done":
                init_dict("received_date", "date")
                if not pline["received_date"] or move.date > pline["received_date"]:
                    pline["received_date"] = move.date
                pline["received_qty"] += move.product_uom_qty
        self._add_computed_fields(lines)
        self.env["reception.checkpoint"].search(
            [("write_uid", "=", self.env.user.id)]
        ).unlink()
        vals = []
        for line in lines.values():
            vals.append(
                (
                    line["product_id"],
                    line["purchase_line_id"],
                    line["purch_line"],
                    line["ordered_qty"],
                    line["write_uid"],
                )
            )
        query = (
            """
        INSERT INTO reception_checkpoint(product_id, purchase_line_id, purch_line, ordered_qty, write_uid)
        VALUES %s
        RETURNING id;
        """
            % vals
        )
        query = query.replace("[", "").replace("]", "")
        self.env.cr.execute(query)
        line_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.browse(line_ids)

    @api.model
    def _add_computed_fields(self, lines):
        for pline, line in lines.items():
            line["diff_qty"] = line["ordered_qty"] - line["received_qty"]
            if not line["purch_line"]:
                line["timing"] = "more"
            elif line["diff_qty"] > 0:
                line["timing"] = "toreceive"
            elif line["diff_qty"] < 0:
                line["timing"] = "more"
            else:
                line["timing"] = "no"
