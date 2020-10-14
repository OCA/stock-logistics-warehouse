# Copyright 2017 Sylvain Van Hoof (Okia) <sylvain@okia.be>
# Copyright 2017-2019 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PutInPackNbr(models.TransientModel):
    _name = 'put.in.pack.nbr'
    _description = 'Put In Pack Number'

    nbr_packages = fields.Integer(
        'Number of packages', required=True, default=1)
    picking_id = fields.Many2one(
        'stock.picking', string='Picking', required=True)

    @api.model
    def default_get(self, fields):
        res = super(PutInPackNbr, self).default_get(fields)
        res.update({'picking_id': self.env.context['active_id']})
        return res

    @api.multi
    def do_put_in_pack(self):
        self.ensure_one()

        return self.picking_id.with_context(
            default_nbr_packages=self.nbr_packages)._put_in_pack()
