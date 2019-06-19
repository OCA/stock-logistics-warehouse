# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    kardex = fields.Boolean()
    parent_is_kardex = fields.Boolean(compute='_compute_parent_is_kardex')
    kardex_tray = fields.Boolean()
    kardex_tray_type_id = fields.Many2one(
        comodel_name="stock.kardex.tray.type", ondelete="restrict"
    )
    kardex_cell_contains_stock = fields.Boolean(
        compute='_compute_kardex_cell_contains_stock',
        help="Used to know if a Kardex location is empty.",
    )
    tray_matrix = fields.Serialized(compute='_compute_tray_matrix')

    # Only for trays cells (boxes).
    # Children of 'kardey_tray' locations, they are automatically generated
    generated_for_tray_type_id = fields.Many2one(
        comodel_name="stock.kardex.tray.type",
        ondelete="restrict",
        readonly=True,
    )

    # TODO document hierarchy + replace "parent_is_kardex" and kardex_tray
    # by an optional selection kardex_view, shuttle, tray, cell
    # Kardex View
    #   -> Shuttle
    #     -> Tray
    #       -> Cell

    @api.depends('quant_ids.quantity')
    def _compute_kardex_cell_contains_stock(self):
        for location in self:
            # TODO replace by check on 'cell' only
            if not location.parent_is_kardex:
                # we skip the others only for performance
                continue
            quants = location.quant_ids.filtered(lambda r: r.quantity > 0)
            location.kardex_cell_contains_stock = bool(quants)

    @api.depends('quant_ids.quantity', 'location_id.kardex_tray_type_id')
    def _compute_tray_matrix(self):
        for location in self:
            if not location.parent_is_kardex:
                continue
            location.tray_matrix = {
                'selected': location._kardex_cell_coords(),
                'cells': location._tray_cells_matrix(),
            }

    @api.depends('location_id.parent_is_kardex')
    def _compute_parent_is_kardex(self):
        for location in self:
            parent = location.location_id
            while parent:
                if parent.kardex:
                    location.parent_is_kardex = True
                    break
                parent = parent.location_id

    @api.model
    def create(self, vals):
        records = super().create(vals)
        if vals.get('kardex_tray'):
            records._update_tray_sublocations()
        return records

    @api.multi
    def write(self, vals):
        result = super().write(vals)
        if vals.get('kardex_tray') or vals.get('kardex_tray_type_id'):
            self._update_tray_sublocations()
        return result

    def _kardex_cell_coords(self):
        # TODO check is a cell
        if not self.generated_for_tray_type_id:  # is a cell
            coords = []
        coords = [self.posx - 1, self.posy - 1]
        return coords

    def _tray_cells_matrix(self):
        assert self.parent_is_kardex
        if self.kardex_tray:
            location = self
        else:
            location = self.location_id
        cells = location.kardex_tray_type_id._generate_cells_matrix()
        for cell in location.child_ids:
            if cell.kardex_cell_contains_stock:
                cells[cell.posy - 1][cell.posx - 1] = 1
        return cells

    @api.multi
    def _update_tray_sublocations(self):
        # TODO: if any sublocation has stock, raise an error,
        # we must be able to change the type of tray only when
        # it is empty
        values = []
        for location in self:
            if not location.kardex_tray:
                sublocs = location.child_ids.filtered(
                    lambda r: r.generated_for_tray_type_id
                )
                sublocs.write({'active': False})
                continue

            tray_type = location.kardex_tray_type_id
            sublocs = location.child_ids.filtered(
                lambda r: r.generated_for_tray_type_id != tray_type
            )
            sublocs.write({'active': False})

            # create accepts several records now
            for row in range(1, tray_type.rows + 1):
                for col in range(1, tray_type.cols + 1):
                    subloc_values = {
                        'name': _('{} [x{} y{}]').format(
                            location.name, col, row
                        ),
                        'posx': col,
                        'posy': row,
                        'location_id': location.id,
                        'company_id': location.company_id.id,
                        'generated_for_tray_type_id': tray_type.id,
                    }
                    values.append(subloc_values)
            self.create(values)
