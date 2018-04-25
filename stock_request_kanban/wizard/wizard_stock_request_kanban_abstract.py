# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, _
from odoo.exceptions import ValidationError
from reportlab.graphics.barcode import getCodes


class WizardStockRequestOrderKanbanAbstract(models.AbstractModel):
    _name = "wizard.stock.request.kanban.abstract"
    _inherit = "barcodes.barcode_events_mixin"

    kanban_id = fields.Many2one(
        'stock.request.kanban',
        readonly=True,
    )
    stock_request_id = fields.Many2one(
        'stock.request',
        readonly=True,
    )
    status = fields.Text(
        readonly=True,
        default="Start scanning",
    )
    status_state = fields.Integer(
        default=0,
        readonly=True,
    )

    def get_barcode_format(self):
        return 'Standard39'

    def validate_barcode(self, barcode):
        bcc = getCodes()[self.get_barcode_format()](value=barcode[:-1])
        bcc.validate()
        bcc.encode()
        if bcc.encoded[1:-1] != barcode:
            raise ValidationError(_('CRC is not valid'))
        return barcode[:-1]

    def on_barcode_scanned(self, barcode):
        barcode = self.validate_barcode(barcode)

        self.kanban_id = self.env['stock.request.kanban'].search([
            ('name', '=', barcode)
        ])
        if not self.kanban_id:
            self.status = _("Barcode %s does not correspond to any "
                            "Kanban. Try with another barcode or "
                            "press Close to finish scanning.") % barcode
            self.status_state = 1
            return
        if self.validate_kanban(barcode):
            self.stock_request_id = self.env['stock.request'].create(
                self.stock_request_kanban_values()
            )
            self.status_state = 0

            self.status = _('Added kanban %s for product %s' % (
                self.stock_request_id.kanban_id.name,
                self.stock_request_id.product_id.display_name
            ))
            self.barcode_ending()
        return

    def barcode_ending(self):
        return

    def validate_kanban(self, barcode):
        '''
        It must return True if the kanban is valid, False otherwise
        :param barcode:
        :return:
        '''
        return True

    def stock_request_kanban_values(self):
        return {
            'company_id': self.kanban_id.company_id.id,
            'procurement_group_id':
                self.kanban_id.procurement_group_id.id or False,
            'location_id': self.kanban_id.location_id.id or False,
            'warehouse_id': self.kanban_id.warehouse_id.id or False,
            'product_id': self.kanban_id.product_id.id,
            'product_uom_id': self.kanban_id.product_uom_id.id or False,
            'route_id': self.kanban_id.route_id.id or False,
            'product_uom_qty': self.kanban_id.product_uom_qty,
            'kanban_id': self.kanban_id.id,
        }
