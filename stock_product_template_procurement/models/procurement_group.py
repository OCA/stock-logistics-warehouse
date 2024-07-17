from odoo import api, models


class ProcurementGroup(models.Model):

    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        newprocurements = []
        for procurement in procurements:
            if not procurement.product_id:
                # this is hacky avoid to overwrite a lot of code
                procurement = procurement._replace(
                    product_id=self.env["product.template"]
                    .browse(procurement.values["product_template_id"])
                    .exists()
                )
            newprocurements.append(procurement)
        return super().run(newprocurements)
