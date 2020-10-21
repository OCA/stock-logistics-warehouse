# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    lot_default_locked = fields.Boolean(
        string="Block new Serial Numbers/lots",
        help="If checked, future Serial Numbers/lots will be created blocked "
        "by default",
    )
