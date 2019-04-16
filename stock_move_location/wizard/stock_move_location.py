# Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2018 Camptocamp SA
# Copyright 2019 Sergio Teruel - Tecnativa <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.fields import first


class StockMoveLocationWizard(models.TransientModel):
    _name = "wiz.stock.move.location"

    origin_location_id = fields.Many2one(
        string='Origin Location',
        comodel_name='stock.location',
        required=True,
        domain=lambda self: self._get_locations_domain(),
    )
    destination_location_id = fields.Many2one(
        string='Destination Location',
        comodel_name='stock.location',
        required=True,
        domain=lambda self: self._get_locations_domain(),
    )
    stock_move_location_line_ids = fields.One2many(
        string="Move Location lines",
        comodel_name="wiz.stock.move.location.line",
        inverse_name="move_location_wizard_id",
    )
    picking_id = fields.Many2one(
        string="Connected Picking",
        comodel_name="stock.picking",
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get('active_model', False) != 'stock.quant':
            return res
        # Load data directly from quants
        quants = self.env['stock.quant'].browse(
            self.env.context.get('active_ids', False))
        res['stock_move_location_line_ids'] = [(0, 0, {
            'product_id': quant.product_id.id,
            'move_quantity': quant.quantity,
            'max_quantity': quant.quantity,
            'origin_location_id': quant.location_id.id,
            'lot_id': quant.lot_id.id,
            'product_uom_id': quant.product_uom_id.id,
            'custom': False,
        }) for quant in quants]
        res['origin_location_id'] = first(quants).location_id.id
        return res

    @api.onchange('origin_location_id')
    def _onchange_origin_location_id(self):
        if not self.env.context.get('origin_location_disable', False):
            self._clear_lines()

    @api.onchange('destination_location_id')
    def _onchange_destination_location_id(self):
        for line in self.stock_move_location_line_ids:
            line.destination_location_id = self.destination_location_id

    def _clear_lines(self):
        self.stock_move_location_line_ids = False

    def _get_locations_domain(self):
        return [('usage', '=', 'internal')]

    def _create_picking(self):
        return self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            'location_id': self.origin_location_id.id,
            'location_dest_id': self.destination_location_id.id,
        })

    @api.multi
    def group_lines(self):
        lines_grouped = {}
        for line in self.stock_move_location_line_ids:
            lines_grouped.setdefault(
                line.product_id.id,
                self.env["wiz.stock.move.location.line"].browse(),
            )
            lines_grouped[line.product_id.id] |= line
        return lines_grouped

    @api.multi
    def _create_moves(self, picking):
        self.ensure_one()
        groups = self.group_lines()
        moves = self.env["stock.move"]
        for lines in groups.values():
            move = self._create_move(picking, lines)
            moves |= move
        return moves

    def _get_move_values(self, picking, lines):
        # locations are same for the products
        location_from_id = lines[0].origin_location_id.id
        location_to_id = lines[0].destination_location_id.id
        product = lines[0].product_id
        product_uom_id = lines[0].product_uom_id.id
        qty = sum([x.move_quantity for x in lines])
        return {
            "name": product.display_name,
            "location_id": location_from_id,
            "location_dest_id": location_to_id,
            "product_id": product.id,
            "product_uom": product_uom_id,
            "product_uom_qty": qty,
            "picking_id": picking.id,
            "location_move": True,
        }

    @api.multi
    def _create_move(self, picking, lines):
        self.ensure_one()
        move = self.env["stock.move"].create(
            self._get_move_values(picking, lines),
        )
        for line in lines:
            line.create_move_lines(picking, move)
        return move

    @api.multi
    def action_move_location(self):
        self.ensure_one()
        picking = self._create_picking()
        self._create_moves(picking)
        if not self.env.context.get("planned"):
            picking.action_confirm()
            picking.action_assign()
            picking.button_validate()
        self.picking_id = picking
        return self._get_picking_action(picking.id)

    def _get_picking_action(self, pickinig_id):
        action = self.env.ref("stock.action_picking_tree_all").read()[0]
        form_view = self.env.ref("stock.view_picking_form").id
        action.update({
            "view_mode": "form",
            "views": [(form_view, "form")],
            "res_id": pickinig_id,
        })
        return action

    def _get_group_quants(self):
        location_id = self.origin_location_id.id
        company = self.env['res.company']._company_default_get(
            'stock.inventory',
        )
        # Using sql as search_group doesn't support aggregation functions
        # leading to overhead in queries to DB
        query = """
            SELECT product_id, lot_id, SUM(quantity)
            FROM stock_quant
            WHERE location_id = %s
            AND company_id = %s
            GROUP BY product_id, lot_id
        """
        self.env.cr.execute(query, (location_id, company.id))
        return self.env.cr.dictfetchall()

    def _get_stock_move_location_lines_values(self):
        product_obj = self.env['product.product']
        product_data = []
        for group in self._get_group_quants():
            product = product_obj.browse(group.get("product_id")).exists()
            product_data.append({
                'product_id': product.id,
                'move_quantity': group.get("sum"),
                'max_quantity': group.get("sum"),
                'origin_location_id': self.origin_location_id.id,
                'destination_location_id': self.destination_location_id.id,
                # cursor returns None instead of False
                'lot_id': group.get("lot_id") or False,
                'product_uom_id': product.uom_id.id,
                'move_location_wizard_id': self.id,
                'custom': False,
            })
        return product_data

    def add_lines(self):
        self.ensure_one()
        line_model = self.env["wiz.stock.move.location.line"]
        if not self.stock_move_location_line_ids:
            for line_val in self._get_stock_move_location_lines_values():
                if line_val.get('max_quantity') <= 0:
                    continue
                line = line_model.create(line_val)
                line.onchange_product_id()
        return {
            "type": "ir.actions.do_nothing",
        }

    def clear_lines(self):
        self._clear_lines()
        return {
            "type": "ir.action.do_nothing",
        }
