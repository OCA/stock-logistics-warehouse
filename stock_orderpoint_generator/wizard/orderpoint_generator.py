# Copyright 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, fields, models
from odoo.exceptions import UserError

_template_register = ["orderpoint_template_id"]


class OrderpointGenerator(models.TransientModel):
    """Wizard defining stock.warehouse.orderpoint configurations for selected
    products. Those configs are generated using templates
    """

    _name = "stock.warehouse.orderpoint.generator"
    _description = "Orderpoint Generator"

    orderpoint_template_id = fields.Many2many(
        comodel_name="stock.warehouse.orderpoint.template",
        relation="order_point_generator_rel",
        string="Reordering Rule Templates",
    )

    def action_configure(self):
        """Action to retrieve wizard data and launch creation of items."""
        self.ensure_one()
        model_obj = self.env[self.env.context.get("active_model")]
        record_ids = model_obj.browse(self.env.context.get("active_ids"))
        if not record_ids:
            return model_obj
        if self.env.context.get("active_model") == "product.template":
            product_ids = record_ids.mapped("product_variant_ids")
            if len(product_ids) != len(record_ids):
                raise UserError(
                    _(
                        "Cannot apply because some of selected "
                        "products has multiple variants."
                    )
                )
            record_ids = product_ids
        self.orderpoint_template_id.create_orderpoints(record_ids)
