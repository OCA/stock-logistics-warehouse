# -*- coding: utf-8 -*-
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import SUPERUSER_ID


def post_init_hook(cr, registry):
    quant_obj = registry['stock.quant']
    quant_ids = quant_obj.search(cr, SUPERUSER_ID, [])
    quant_obj.merge_stock_quants(cr, SUPERUSER_ID, quant_ids)
