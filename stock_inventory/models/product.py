from odoo import _, api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_inventory(self):
        """ Retrieve template's product.product
            and call `product.product.action_inventory`
        """
        products = self.env['product.product'].search(
            [('product_tmpl_id', 'in', self._context.get('active_ids'))]
        )
        return self.env['product.product'].action_inventory(products.ids)

class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_inventory(self, product_ids=None):
        """ Create an inventory group from a selection of records
            and redirect the user to the created inventory's form
        """
        product_ids = product_ids or self._context.get('active_ids')

        # create inventory
        inventory = self.env['stock.inventory'].create({
            'product_selection': 'manual',
            'product_ids': product_ids,
        })

        # redirect the user
        action_id = 'stock_inventory.action_view_inventory_group_form'
        return self.env['ir.actions.act_window']._for_xml_id(action_id) | {
            'res_id': inventory.id,
            'views': [(False, 'form')],
        }
