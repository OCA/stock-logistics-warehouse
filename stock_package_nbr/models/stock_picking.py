# Copyright 2017 Sylvain Van Hoof (Okia) <sylvain@okia.be>
# Copyright 2018-2019 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def put_in_pack_nbr(self):
        self.ensure_one()
        if not self.move_line_ids.filtered(
                lambda o: o.qty_done > 0 and not o.result_package_id):
            # let's raise the standard error
            return self.put_in_pack()
        return self.env.ref('stock_package_nbr.put_in_pack_nbr').read()[0]

    nbr_packages = fields.Integer('Number of packages', default=1)
