# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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


from openerp import api, fields, models


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    uom_id = fields.Many2one('product.uom', 'Unit of Measure', required=True,
                             help="It must be in the same category than "
                             "the default unit of measure.")
    uom_categ_domain_id = fields.Many2one(
        related='product_tmpl_id.uom_id.category_id',
        comodel_name='product.uom.categ')
    qty = fields.Float(compute="_compute_qty", store=True, readonly=True)

    @api.one
    @api.depends('uom_id', 'product_tmpl_id.uom_id')
    def _compute_qty(self):
        """
        Compute the quantity by package based on uom
        """
        if self.uom_id and self.product_tmpl_id:
            self.qty = self.env['product.uom']._compute_qty_obj(
                self.uom_id, 1, self.product_tmpl_id.uom_id)
        else:
            self.qty = 0
