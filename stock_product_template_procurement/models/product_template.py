from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_description(self, picking_type_id):
        """return product receipt/delivery/picking description depending on
        picking type passed as argument.
        """
        self.ensure_one()
        picking_code = picking_type_id.code
        description = self.description or self.name
        if picking_code == "incoming":
            return self.description_pickingin or description
        if picking_code == "outgoing":
            return self.description_pickingout or self.name
        if picking_code == "internal":
            return self.description_picking or description
        return description
