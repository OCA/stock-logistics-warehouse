# Copyright 2018 Camptocamp SA
# Copyright 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# Copyright 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from lxml import etree


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_putaway_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='product_tmpl_id',
        string="Product stock locations",
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_putaway_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='product_product_id',
        string="Product stock locations",
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """ Custom redefinition of fields_view_get to adapt the context
            to product variants.
        """
        res = super().fields_view_get(view_id=view_id,
                                      view_type=view_type,
                                      toolbar=toolbar,
                                      submenu=submenu)
        if view_type == 'form':
            product_xml = etree.XML(res['arch'])
            putaway_path = "//field[@name='product_putaway_ids']"
            putaway_fields = product_xml.xpath(putaway_path)
            if putaway_fields:
                putaway_field = putaway_fields[0]
                putaway_field.attrib['context'] = \
                    "{'default_product_tmpl_id': product_tmpl_id," \
                    "'default_product_product_id': active_id}"
                res['arch'] = etree.tostring(product_xml)

        return res
