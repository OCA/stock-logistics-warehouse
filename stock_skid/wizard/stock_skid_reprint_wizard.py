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
from openerp.tools.float_utils import float_compare


class SkidReprintWizard(orm.TransientModel):
    _name = "stock.skid.reprint.wizard"
    _description = "Skid Reprint Wizard"
    _columns = {
        "prodlot_id": fields.many2one("stock.production.lot", "Production Lot"),
        "location_id": fields.many2one("stock.location", "Location"),
        "packer_name": fields.char('Packer', size=64),
        "new_quantity": fields.integer("New Quantity"),
    }

    def do_print(self, cr, uid, ids, context=None):
        inv_obj = self.pool["report.stock.inventory"]
        location_obj = self.pool["stock.location"]
        move_obj = self.pool["stock.move"]
        user_obj = self.pool["res.users"]

        # We expect ids to be a list with one element
        form = self.browse(cr, uid, ids[0], context=context)
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
            if lot["location_id"][0] == form.location_id.id
        ]

        current_qty = lot_info[0]["product_qty"] if lot_info else 0
        new_quantity = form.new_quantity

        product = form.prodlot_id.product_id
        uom_rounding = product.uom_id.rounding
        compare_qty = float_compare(current_qty, new_quantity,
                                    precision_rounding=uom_rounding)
        if compare_qty != 0:
            inv_loss = location_obj.search(cr, uid, [
                ('usage', '=', 'inventory'), ('scrap_location', '=', False),
            ], limit=1)
            if not inv_loss:
                raise orm.except_orm(
                    _("No Inventory Loss Location"),
                    _("Please configure a location with usage = inventory"
                      " and scrap_location=False"),
                )
            inv_loss_name = location_obj.browse(cr, uid, inv_loss[0],
                                                context=context).name

            create = {
                "product_qty": abs(current_qty - new_quantity),
                "product_id": product.id,
                "prodlot_id": form.prodlot_id.id,
                "product_uom": product.uom_id.id,
                "state": "done",
            }
            if compare_qty > 0:  # current > new_quantity
                # Need to move some stock to inventory loss
                create.update({
                    "location_id": form.location_id.id,
                    "location_dest_id": inv_loss[0],
                    "name": "{0} > {1}".format(form.location_id.name,
                                               inv_loss_name),
                })
            else:
                # Need to move some stock from inventory loss
                create.update({
                    "location_dest_id": form.location_id.id,
                    "location_id": inv_loss[0],
                    "name": "{0} > {1}".format(inv_loss_name,
                                               form.location_id.name),
                })
            move_obj.create(cr, uid, create, context=context)

        label_data = [
            {"product_qty": new_quantity,
             "supervisor": supervisor.name,
             "company_name": supervisor.company_id.name,
             }
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
