from odoo import models, fields, api


class SaleStockReserve(models.TransientModel):
    _name = 'sale.stock.reserve'
    _description = 'Sale Stock Reservation'

    date_validity = fields.Date(
        "Validity Date",
        help="If a date is given, the reservations will be released "
             "at the end of the validity.")
    note = fields.Text('Notes')

    @api.model
    def _get_so_lines(self):
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')
        active_id = self.env.context.get('active_id')

        if active_model == 'sale.order' and active_id:
            lines = self.env[active_model].browse(active_id).order_line
        elif active_model == 'sale.order.line' and active_ids:
            lines = self.env[active_model].browse(active_ids)
        else:
            lines = self.env['sale.order.line'].browse()

        return lines

    @api.multi
    def button_reserve(self):
        self.ensure_one()

        lines = self._get_so_lines()
        if lines:
            lines.acquire_stock_reservation(date_validity=self.date_validity,
                                            note=self.note)

        return {'type': 'ir.actions.act_window_close'}
