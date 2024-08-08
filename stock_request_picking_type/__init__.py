# Copyright 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from . import models

def post_init_hook(cr, registry):
    from .models.stock_warehouse import update_stock_request_type
    update_stock_request_type(cr, registry)
