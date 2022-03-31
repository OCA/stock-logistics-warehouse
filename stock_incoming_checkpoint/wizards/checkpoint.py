# -*- coding: utf-8 -*-
# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from openerp import models, api, fields


class IncomingCheckpoint(models.TransientModel):
    _name = "incoming.checkpoint"
    _description = "Incoming checkpoint"

    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    partner_ref = fields.Char(compute="_compute_partner_ref")
    date_planned = fields.Date(string="Schedule Date")
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
    color = fields.Char(help="Technical field to apply color in tree view")
    awaiting_move_id = fields.Many2one(comodel_name="stock.move")

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
        lines = defaultdict(dict)
        line_ids = []
        uid = self.env.user.id
        for move in moves:
            if move.purchase_line_id in lines:
                pline = lines[move.purchase_line_id]
                pline.update({"move": move})
            else:
                pline = lines[move.purchase_line_id]
                pline.update(
                    {
                        "product_id": move.product_id.id,
                        "purchase_line_id": move.purchase_line_id.id,
                        "purch_line": move.purchase_line_id
                        and move.purchase_line_id.id
                        or False,
                        "date_planned": move.purchase_line_id.date_planned,
                        "ordered_qty": move.purchase_line_id.product_qty,
                        "order_id": move.purchase_line_id.order_id.id,
                        "write_uid": uid,
                        "move": move,
                        "awaiting_move_id": None,
                    }
                )
            if move.state not in ("done", "cancel", "draft"):
                pline["awaiting_move_id"] = move.id
            if "received_qty" not in pline:
                pline["received_qty"] = 0
            if move.state == "done":
                if "received_date" not in pline:
                    pline["received_date"] = False
                if not pline["received_date"] or move.date > pline["received_date"]:
                    pline["received_date"] = move.date
                pline["received_qty"] += move.product_uom_qty
        self._add_computed_fields(lines)
        self.env["incoming.checkpoint"].search(
            [("write_uid", "=", self.env.user.id)]
        ).unlink()
        query = self._prepare_create(lines)
        query = query.replace("[", "").replace("]", "")
        self.env.cr.execute(query)
        line_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.browse(line_ids)

    def _prepare_create(self, lines):
        vals = []
        for line in lines.values():
            vals.append(tuple(self._get_column_vals(line)))
        query = """
        %s
        VALUES %s
        RETURNING id;
        """ % (
            self._get_insert_into_columns(),
            vals,
        )
        return query.replace("None", "NULL").replace("[", "").replace("]", "")

    def _get_column_vals(self, line):
        """Inherit to complete columns"""
        return [
            line["product_id"],
            line["purchase_line_id"],
            line["purch_line"],
            line["date_planned"],
            line["ordered_qty"],
            line["received_qty"],
            line["diff_qty"],
            line["write_uid"],
            line["color"],
            line["awaiting_move_id"],
        ]

    def _get_insert_into_columns(self):
        """Inherit to complete columns"""
        return """INSERT INTO incoming_checkpoint(product_id, purchase_line_id,
        purch_line, date_planned, ordered_qty, received_qty, diff_qty,
        write_uid, color, awaiting_move_id)"""

    @api.model
    def _add_computed_fields(self, lines):
        for pline, line in lines.items():
            line["diff_qty"] = line["ordered_qty"] - line["received_qty"]
            if not line["purch_line"]:
                line["color"] = "more"
            elif line["diff_qty"] > 0:
                line["color"] = "toreceive"
            elif line["diff_qty"] < 0:
                line["color"] = "more"
            else:
                line["color"] = "no"
