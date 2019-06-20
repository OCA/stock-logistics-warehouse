# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.addons.base_sparse_field.models.fields import Serialized


class StockLocation(models.Model):
    _inherit = "stock.location"

    kardex_location = fields.Boolean(
        'Is a Kardex View Location?',
        default=False,
        help="Check this box to use it as the view for Kardex shuttles.",
    )
    kardex_kind = fields.Selection(
        selection=[
            ('view', 'View'),
            ('shuttle', 'Shuttle'),
            ('tray', 'Tray'),
            ('cell', 'Cell'),
        ],
        compute='_compute_kardex_kind',
        store=True,
    )
    kardex_tray_type_id = fields.Many2one(
        comodel_name="stock.kardex.tray.type", ondelete="restrict"
    )
    kardex_cell_contains_stock = fields.Boolean(
        compute='_compute_kardex_cell_contains_stock',
        help="Used to know if a Kardex location is empty.",
    )
    tray_matrix = Serialized(compute='_compute_tray_matrix')

    # TODO document hierarchy
    # by an optional selection kardex_view, shuttle, tray, cell
    # Kardex View
    #   -> Shuttle
    #     -> Tray
    #       -> Cell

    @api.depends('location_id', 'location_id.kardex_kind')
    def _compute_kardex_kind(self):
        tree = {'view': 'shuttle', 'shuttle': 'tray', 'tray': 'cell'}
        for location in self:
            if location.kardex_location:
                location.kardex_kind = 'view'
                continue
            kind = tree.get(location.location_id.kardex_kind)
            if kind:
                location.kardex_kind = kind

    @api.depends('quant_ids.quantity')
    def _compute_kardex_cell_contains_stock(self):
        for location in self:
            if not location.kardex_kind == 'cell':
                # we skip the others only for performance
                continue
            quants = location.quant_ids.filtered(lambda r: r.quantity > 0)
            location.kardex_cell_contains_stock = bool(quants)

    @api.depends(
        'quant_ids.quantity',
        'kardex_tray_type_id',
        'location_id.kardex_tray_type_id',
    )
    def _compute_tray_matrix(self):
        for location in self:
            if location.kardex_kind not in ('tray', 'cell'):
                continue
            location.tray_matrix = {
                'selected': location._kardex_cell_coords(),
                'cells': location._tray_cells_matrix(),
            }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._update_tray_sublocations()
        return records

    @api.multi
    def write(self, vals):
        for location in self:
            trays_to_update = False
            if 'kardex_tray_type_id' in vals:
                new_tray_type_id = vals.get('kardex_tray_type_id')
                trays_to_update = (
                    location.kardex_tray_type_id.id != new_tray_type_id
                )
            super(StockLocation, location).write(vals)
            if trays_to_update:
                self._update_tray_sublocations()
        return True

    @api.constrains('active')
    def _stock_kardex_check_active(self):
        for record in self:
            if not record.kardex_kind:
                continue
            if record.active:
                continue
            # We cannot disable any cell of a tray (entire tray)
            # if at least one of the cell contains stock.
            # We cannot disable a tray, a shuffle or a view if
            # at least one of their tray contain stock.
            if record.kardex_kind == 'cell':
                parent = record.location_id
            else:
                parent = record
            locs = self.search([('id', 'child_of', parent.id)])
            if any(loc.kardex_cell_contains_stock for loc in locs):
                raise exceptions.ValidationError(
                    _(
                        "Kardex locations cannot be archived when "
                        "they contain products."
                    )
                )

    def _kardex_cell_coords(self):
        if not self.kardex_kind == 'cell':
            coords = []
        coords = [self.posx - 1, self.posy - 1]
        return coords

    def _tray_cells_matrix(self):
        assert self.kardex_kind in ('tray', 'cell')
        if self.kardex_kind == 'tray':
            location = self
        else:  # cell
            location = self.location_id
        cells = location.kardex_tray_type_id._generate_cells_matrix()
        for cell in location.child_ids:
            if cell.kardex_cell_contains_stock:
                cells[cell.posy - 1][cell.posx - 1] = 1
        return cells

    @api.multi
    def _update_tray_sublocations(self):
        values = []
        for location in self:
            if not location.kardex_kind == 'tray':
                continue

            tray_type = location.kardex_tray_type_id

            try:
                location.child_ids.write({'active': False})
            except exceptions.ValidationError:
                # trap this check (_stock_kardex_check_active) to display a
                # contextual error message
                raise exceptions.ValidationError(
                    _(
                        "Kardex trays cannot be modified when "
                        "they contain products."
                    )
                )
            if not tray_type:
                continue

            # create accepts several records now
            for row in range(1, tray_type.rows + 1):
                for col in range(1, tray_type.cols + 1):
                    subloc_values = {
                        'name': _('x{}y{}').format(col, row),
                        'posx': col,
                        'posy': row,
                        'location_id': location.id,
                        'company_id': location.company_id.id,
                    }
                    values.append(subloc_values)
        if values:
            self.create(values)

    @api.multi
    def _create_tray_xmlids(self):
        """Create external IDs for generated cells

        Called from stock/kardex/demo/stock_location_demo.xml.

        If the tray has one. Used for the demo/test data. It will not handle
        properly changing the tray format as the former cells will keep the
        original xmlid built on x and y, the new ones will not be able to used
        them. As these xmlids are meant for the demo data and the tests, it is
        not a problem and should not be used for other purposes.
        """
        for location in self:
            if location.kardex_kind != 'cell':
                continue
            tray = location.location_id
            tray_external_id = tray.get_external_id().get(tray.id)
            if not tray_external_id:
                continue
            if '.' not in tray_external_id:
                continue
            module, tray_name = tray_external_id.split('.')
            tray_external = self.env['ir.model.data'].browse(
                self.env['ir.model.data']._get_id(module, tray_name)
            )
            cell_external_id = "{}_x{}y{}".format(
                tray_name, location.posx, location.posy
            )
            if not self.env.ref(cell_external_id, raise_if_not_found=False):
                self.env['ir.model.data'].create(
                    {
                        'name': cell_external_id,
                        'module': module,
                        'model': self._name,
                        'res_id': location.id,
                        'noupdate': tray_external.noupdate,
                    }
                )
