# Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


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

    @api.onchange('origin_location_id', 'destination_location_id')
    def _onchange_locations(self):
        self._clear_lines()

    def _clear_lines(self):
        origin = self.origin_location_id
        destination = self.destination_location_id
        # there is `invalidate_cache` call inside the unlink
        # which will clear the wizard - not cool.
        # we have to keep the values somehow
        self.stock_move_location_line_ids.unlink()
        self.origin_location_id = origin
        self.destination_location_id = destination

    def _get_locations_domain(self):
        return [('usage', '=', 'internal')]

    def _create_picking(self):
        return self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            'location_id': self.origin_location_id.id,
            'location_dest_id': self.destination_location_id.id,
        })

    def _create_moves(self, picking):
        return self.stock_move_location_line_ids.create_move_lines(picking)

    @api.multi
    def action_move_location(self):
        self.ensure_one()
        picking = self._create_picking()
        self._create_moves(picking)
        if not self.env.context.get("planned"):
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

    def _get_group_quants_sql(self):
        location_id = self.origin_location_id.id
        company = self.env['res.company']._company_default_get(
            'stock.inventory',
        )
        return """
        SELECT product_id, lot_id, SUM(quantity)
        FROM stock_quant
        WHERE location_id = {location_id} AND company_id = {company_id}
        GROUP BY product_id, lot_id
        """.format(
            location_id=location_id,
            company_id=company.id,
        )

    def _get_stock_move_location_lines_values(self):
        product_obj = self.env['product.product']

        # Using sql as search_group doesn't support aggregation functions
        # leading to overhead in queries to DB
        self.env.cr.execute(self._get_group_quants_sql())
        product_data = []
        for group in self.env.cr.dictfetchall():
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
            })
        return product_data

    def add_lines(self):
        self.ensure_one()
        if not self.stock_move_location_line_ids:
            for line_val in self._get_stock_move_location_lines_values():
                self.env["wiz.stock.move.location.line"].create(line_val).id
        return {
            "type": "ir.actions.do_nothing",
        }

    def clear_lines(self):
        self._clear_lines()
        return {
            "type": "ir.action.do_nothing",
        }
