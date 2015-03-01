from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp

class StockProductionLot(orm.Model):

    def _validate_retained_stock(self, cr, uid, ids, context=None):   
        for lot in self.browse(cr, uid, ids, context=context):
            if lot.retained_stock < 0:
                return False

        return True

    _inherit = "stock.production.lot"

    _columns = {
        'retained_stock': fields.float(string='Retained stock'),
    }

    _constraints = [
        (
            _validate_retained_stock,
            'Retained stock cannot be negative',
            ['retained_stock'],
        ),
    ]
