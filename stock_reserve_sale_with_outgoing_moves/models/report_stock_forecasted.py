# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models
from odoo.osv import expression


class ReplenishmentReport(models.AbstractModel):
    _inherit = "report.stock.report_product_product_replenishment"

    def _product_sale_domain(self, product_template_ids, product_variant_ids):
        domain = super()._product_sale_domain(product_template_ids, product_variant_ids)
        domain = expression.AND([domain, [("order_id.stock_is_reserved", "=", False)]])
        return domain
