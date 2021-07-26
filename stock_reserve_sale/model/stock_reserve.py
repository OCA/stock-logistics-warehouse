##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class StockReservation(models.Model):
    _inherit = "stock.reservation"

    sale_line_id = fields.Many2one(
        "sale.order.line", string="Sale Order Line", ondelete="cascade", copy=False
    )
    sale_id = fields.Many2one(
        "sale.order", string="Sale Order", related="sale_line_id.order_id"
    )

    @api.multi
    def release(self):
        for rec in self:
            rec.sale_line_id = False
        return super(StockReservation, self).release()
