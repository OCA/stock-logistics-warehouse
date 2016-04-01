# -*- coding: utf-8 -*-

from . import models


def set_product_purchase_qty(cr, registry):
    cr.execute("""update purchase_order_line
                  set product_purchase_qty = product_qty""")
