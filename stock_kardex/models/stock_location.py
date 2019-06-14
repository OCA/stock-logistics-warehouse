# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    kardex_tray = fields.Boolean()
    kardex_tray_type_id = fields.Many2one(
        comodel_name="stock.kardex.tray.type", ondelete="restrict"
    )

    # Only for trays cells (boxes).
    # Children of 'kardey_tray' locations, they are automatically generated
    generated_for_tray_type_id = fields.Many2one(
        comodel_name="stock.kardex.tray.type",
        ondelete="restrict",
        readonly=True,
    )

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
