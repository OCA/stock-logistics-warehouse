# Copyright 2020 Camptocamp SA.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openerp import models, fields, api, exceptions


class SaleStockReserve(models.TransientModel):
    _name = 'sale.stock.reserve'

    @api.model
    def _default_location_id(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        browse_model = self.env[active_model].browse(active_id)
        if active_model == 'sale.order.line':
            browse_model = browse_model.order_id
        return browse_model.warehouse_id.pick_type_id.\
            default_location_src_id.id

    @api.model
    def _default_location_dest_id(self):
        return self.env['stock.reservation']._default_location_dest_id()

    def _default_owner(self):
        """If sale_owner_stock_sourcing is installed, it adds an owner field
        on sale order lines. Use it.

        """
        model = self.env[self.env.context['active_model']]
        if model._name == 'sale.order':
            lines = model.browse(self.env.context['active_id']).order_line
        else:
            lines = model.browse(self.env.context['active_ids'])

        try:
            owners = set([l.stock_owner_id for l in lines])
        except AttributeError:
            return self.env['res.partner']
            # module sale_owner_stock_sourcing not installed, fine

        if len(owners) == 1:
            return owners.pop()
        elif len(owners) > 1:
            raise exceptions.Warning(
                'The lines have different owners. Please reserve them '
                'individually with the reserve button on each one.')

        return self.env['res.partner']

    location_id = fields.Many2one(
        'stock.location',
        'Source Location',
        required=True,
        default=_default_location_id
        )
    location_dest_id = fields.Many2one(
        'stock.location',
        'Reservation Location',
        required=True,
        help="Location where the system will reserve the "
             "products.",
        default=_default_location_dest_id)
    date_validity = fields.Date(
        "Validity Date",
        help="If a date is given, the reservations will be released "
             "at the end of the validity.")
    note = fields.Text('Notes')
    owner_id = fields.Many2one('res.partner', 'Stock Owner',
                               default=_default_owner)

    @api.multi
    def _prepare_stock_reservation(self, line):
        self.ensure_one()
        return {
            'product_id': line.product_id.id,
            'product_uom': line.product_uom.id,
            'product_uom_qty': line.product_uom_qty,
            'date_validity': self.date_validity,
            'name': "%s (%s)" % (line.order_id.name, line.name),
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'note': self.note,
            'price_unit': line.price_unit,
            'sale_line_id': line.id,
            'restrict_partner_id': self.owner_id.id,
        }

    @api.multi
    def stock_reserve(self, line_ids):
        self.ensure_one()
        lines = self.env['sale.order.line'].browse(line_ids)
        reserv = self.env['stock.reservation']
        for line in lines:
            if not line.is_stock_reservable:
                continue
            vals = self._prepare_stock_reservation(line)
            reserv |= self.env['stock.reservation'].create(vals)
        if reserv:
            reserv.reserve()
        return True

    @api.multi
    def button_reserve(self):
        env = self.env
        self.ensure_one()
        close = {'type': 'ir.actions.act_window_close'}
        active_model = env.context.get('active_model')
        active_ids = env.context.get('active_ids')
        if not (active_model and active_ids):
            return close

        if active_model == 'sale.order':
            sales = env['sale.order'].browse(active_ids)
            line_ids = [line.id for sale in sales for line in sale.order_line]

        if active_model == 'sale.order.line':
            line_ids = active_ids

        self.stock_reserve(line_ids)
        return close
