# -*- encoding: utf-8 -*-

############################################################################
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class SkidReprintWizard(orm.TransientModel):
    _name = "stock.skid.reprint.wizard"
    _description = "Skid Reprint Wizard"
    _columns = {
        "prodlot_id": fields.many2one("stock.production.lot", "Production Lot"),
        "location_id": fields.many2one("stock.location", "Location"),
        "packer_name": fields.char('Packer', size=64),
    }

    def do_print(self, cr, uid, ids, context=None):
        # We expect ids to be a list with one element
        form = self.browse(cr, uid, ids[0], context=context)
        inv_obj = self.pool["report.stock.inventory"]
        user_obj = self.pool["res.users"]
        supervisor = user_obj.browse(cr, uid, uid, context=context)
        lot_info = [
            lot for lot in inv_obj.read_group(
                cr, uid, [
                    # Do NOT filter on location_id, it messes up counts
                    ('prodlot_id', '=', form.prodlot_id.id),
                ],
                fields=["product_qty", "location_id"],
                groupby=["location_id"],
                context=context,
            )
            if (lot["location_id"][0] == form.location_id.id and
                lot["product_qty"] > 0)
        ]
        if not lot_info:
            raise orm.except_orm(
                _("No available lot"),
                _("This production lot was not found at the requested"
                  " location"),
            )

        label_data = [
            {"product_qty": lot["product_qty"],
             "supervisor": supervisor.name,
             "company_name": supervisor.company_id.name,
             }
            for lot in lot_info
        ]
        ctx = {}
        ctx["label_data"] = label_data

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'stock_skid.report.skid_label',
            'context': ctx,
            'datas': {
                'model': self._name,
                'id': ids and ids[0],
                'ids': ids,
                'report_type': 'pdf'
            },
            'nodestroy': True
        }
