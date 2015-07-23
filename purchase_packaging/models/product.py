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


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model
    def _default_min_qty_uom_id(self):
        return self.env.ref('product.product_uom_unit')

    packaging_id = fields.Many2one('product.packaging', 'Logisitical Units')
    product_uom = fields.Many2one(compute='_compute_product_uom',
                                  string="Supplier Unit of Measure",
                                  readonly=True)
    min_qty_uom_id = fields.Many2one('product.uom',
                                     'Minimal Unit of Measure Quantity',
                                     required=True,
                                     default=_default_min_qty_uom_id)

    @api.one
    @api.depends('product_tmpl_id', 'packaging_id')
    def _compute_product_uom(self):
        """ Set product_uom as a computed field instead of a related field.
            To use uom of link packaging
        """
        self.product_uom = self.packaging_id.uom_id or \
            self.product_tmpl_id.uom_po_id
