# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MakeProcurementOrderpoint(models.TransientModel):
    _name = 'make.procurement.orderpoint'
    _description = 'Make Procurements from Orderpoints'

    item_ids = fields.One2many(
        'make.procurement.orderpoint.item',
        'wiz_id', string='Items')

    @api.model
    def _prepare_item(self, orderpoint):
        return {
            'qty': orderpoint.procure_recommended_qty,
            'uom_id': orderpoint.product_uom.id,
            'orderpoint_id': orderpoint.id,
            'product_id': orderpoint.product_id.id,
            'warehouse_id': orderpoint.warehouse_id.id,
            'location_id': orderpoint.location_id.id
        }

    @api.model
    def default_get(self, fields):
        res = super(MakeProcurementOrderpoint, self).default_get(fields)
        orderpoint_obj = self.env['stock.warehouse.orderpoint']
        orderpoint_ids = self.env.context['active_ids'] or []
        active_model = self.env.context['active_model']

        if not orderpoint_ids:
            return res
        assert active_model == 'stock.warehouse.orderpoint', \
            'Bad context propagation'

        items = []
        for line in orderpoint_obj.browse(orderpoint_ids):
            items.append([0, 0, self._prepare_item(line)])
        res['item_ids'] = items
        return res

    @api.multi
    def make_procurement(self):
        self.ensure_one()
        errors = []
        for item in self.item_ids:
            if not item.qty:
                raise ValidationError(_("Quantity must be positive."))
            if not item.orderpoint_id:
                raise ValidationError(_("No reordering rule found!"))
            values = item.orderpoint_id._prepare_procurement_values(item.qty)
            # Run procurement
            try:
                self.env['procurement.group'].run(
                    item.orderpoint_id.product_id,
                    item.qty,
                    item.orderpoint_id.product_uom,
                    item.orderpoint_id.location_id,
                    item.orderpoint_id.name,
                    item.orderpoint_id.name,
                    values
                )
            except UserError as error:
                    errors.append(error.name)
            if errors:
                raise UserError('\n'.join(errors))

        return {'type': 'ir.actions.act_window_close'}


class MakeProcurementOrderpointItem(models.TransientModel):
    _name = 'make.procurement.orderpoint.item'
    _description = 'Make Procurements from Orderpoint Item'

    wiz_id = fields.Many2one(
        'make.procurement.orderpoint', string='Wizard', required=True,
        ondelete='cascade', readonly=True)

    qty = fields.Float(string='Quantity', required=True)

    uom_id = fields.Many2one(string='Unit of Measure',
                             comodel_name='product.uom')
    date_planned = fields.Date(string='Planned Date', required=False)

    orderpoint_id = fields.Many2one(string='Reordering rule',
                                    comodel_name='stock.warehouse.orderpoint',
                                    readonly=False)
    product_id = fields.Many2one(string='Product',
                                 comodel_name='product.product',
                                 readonly=True)
    warehouse_id = fields.Many2one(string='Warehouse',
                                   comodel_name='stock.warehouse',
                                   readonly=True)
    location_id = fields.Many2one(string='Location',
                                  comodel_name='stock.location',
                                  readonly=True)

    @api.multi
    @api.onchange('uom_id')
    def onchange_uom_id(self):
        for rec in self:
            rec.qty = rec.orderpoint_id.product_uom._compute_quantity(
                rec.orderpoint_id.procure_recommended_qty,
                rec.uom_id)
