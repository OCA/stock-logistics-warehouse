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

    def action_move_location(self):
        inventory_obj = self.env["stock.inventory"]
        collected_inventory = inventory_obj.create(
            self._get_collected_inventory_values()
        )
        collected_inventory.action_start()
        self.set_inventory_lines(collected_inventory)
        collected_inventory.move_stock()
        return self._get_inventory_action(collected_inventory.id)

    def _get_collected_inventory_name(self):
        sequence = self.env['ir.sequence'].next_by_code(
            'stock.inventory.move') or '/'
        res = "{sequence}:{location_from}:{location_to}".format(
            sequence=sequence,
            location_from=self.origin_location_id.display_name,
            location_to=self.destination_location_id.display_name,
        )
        return res

    def _get_collected_inventory_values(self):
        return {
            "name": self._get_collected_inventory_name(),
            "location_id": self.origin_location_id.id,
            "inventory_type": "move",
            "destination_location_id": self.destination_location_id.id,
            "filter": "partial",
        }

    def _get_inventory_action(self, inventory_id):
        action = self.env.ref("stock.action_inventory_form").read()[0]
        form_view = self.env.ref("stock.view_inventory_form").id
        action.update({
            "view_mode": "form",
            "views": [(form_view, "form")],
            "res_id": inventory_id,
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

    def _get_inventory_lines_values(self, inventory):
        self.ensure_one()
        lines = []
        for wizard_line in self.stock_move_location_line_ids:
            lines.append({
                'product_id': wizard_line.product_id.id,
                'product_uom_id': wizard_line.product_uom_id.id,
                'prod_lot_id': wizard_line.lot_id.id,
                'product_qty': self._get_available_quantity(wizard_line),
                'inventory_id': inventory.id,
                'location_id': self.origin_location_id.id,
            })
        return lines

    def set_inventory_lines(self, inventory):
        inventory_line_obj = self.env["stock.inventory.line"]
        for line_vals in self._get_inventory_lines_values(inventory):
            inventory_line_obj.create(line_vals)

    def _get_available_quantity(self, line):
        """We check here if the actual amount changed in the stock.

        We don't care about the reservations but we do care about not moving
        more than exists."""
        if not line.product_id:
            return 0
        # switched to sql here to improve performance and lower db queries
        self.env.cr.execute(self._get_specific_quants_sql(line))
        available_qty = self.env.cr.fetchone()[0]
        if available_qty < line.move_quantity:
            return available_qty
        return line.move_quantity

    def _get_specific_quants_sql(self, line):
        lot = "AND lot_id = {}".format(line.lot_id.id)
        if not line.lot_id:
            lot = "AND lot_id is null"
        return """
        SELECT sum(quantity)
        FROM stock_quant
        WHERE location_id = {location}
        {lot}
        AND product_id = {product}
        GROUP BY location_id, product_id, lot_id
        """.format(
            location=line.origin_location_id.id,
            product=line.product_id.id,
            lot=lot,
        )
