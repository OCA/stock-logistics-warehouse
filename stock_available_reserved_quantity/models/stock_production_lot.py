from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp

def get_stock_proxy(self, cr, uid, ids, field_name, arg, context=None):
    return self._get_stock(cr, uid, ids, field_name, arg, context=context)

def stock_search_proxy(self, cr, uid, obj, name, args, context=None):
    return self._stock_search(cr, uid, obj, name, args, context=context)

class StockProductionLot(orm.Model):

    def _validate_retained_stock(self, cr, uid, ids, context=None):   
        for lot in self.browse(cr, uid, ids, context=context):
            if lot.retained_stock < 0:
                return False

        return True

    _inherit = "stock.production.lot"

    _columns = {
        'stock_available': fields.function(
            get_stock_proxy,
            fnct_search=stock_search_proxy,
            type="float",
            string="Available",
            select=True,
            help="Current quantity of products with this Serial Number "
                 "available in company warehouses",
            digits_compute=dp.get_precision('Product Unit of Measure')
        ),
        'retained_stock': fields.float(string='Retained stock'),
    }

    _constraints = [
        (
            _validate_retained_stock,
            'Retained stock cannot be negative',
            ['retained_stock'],
        ),
    ]

    def _get_stock(self, cr, uid, ids, field_name, arg, context=None):

        base_func = super(StockProductionLot, self)._get_stock
        res = base_func(cr, uid, ids, field_name, arg, context=context)
        ids = res.keys()

        for prod_lot in self.browse(cr, uid, ids):
            res[prod_lot.id] -= prod_lot.retained_stock

        return res
