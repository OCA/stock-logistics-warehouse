# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import defaultdict

from odoo import SUPERUSER_ID, _, api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        return [*super()._get_custom_move_fields(), "product_template_id"]

    @api.model
    def _run_pull_product_template(self, product_template_procurements):

        moves_values_by_company = defaultdict(list)
        mtso_products_by_locations = defaultdict(list)

        # To handle the `mts_else_mto` procure method, we do a preliminary loop to
        # isolate the products we would need to read the forecasted quantity,
        # in order to to batch the read. We also make a sanitary check on the
        # `location_src_id` field.
        for procurement, rule in product_template_procurements:
            if not rule.location_src_id:
                msg = _("No source location defined on stock rule: %s!") % (rule.name,)
                raise ProcurementException([(procurement, msg)])

            if rule.procure_method == "mts_else_mto":
                mtso_products_by_locations[rule.location_src_id].append(
                    procurement.product_id.id
                )

        # Get the forecasted quantity for the `mts_else_mto` procurement.
        forecasted_qties_by_loc = {}
        for location, product_tmpl_ids in mtso_products_by_locations.items():
            products = (
                self.env["product.template"]
                .browse(product_tmpl_ids)
                .product_ids.with_context(location=location.id)
            )
            forecasted_qties_by_loc[location] = {
                product.id: product.free_qty for product in products
            }

        # Prepare the move values, adapt the `procure_method` if needed.
        for procurement, rule in product_template_procurements:
            procure_method = rule.procure_method
            if rule.procure_method == "mts_else_mto":
                qty_needed = procurement.product_uom._compute_quantity(
                    procurement.product_qty, procurement.product_id.uom_id
                )
                qty_available = forecasted_qties_by_loc[rule.location_src_id][
                    procurement.product_id.id
                ]
                if (
                    float_compare(
                        qty_needed,
                        qty_available,
                        precision_rounding=procurement.product_id.uom_id.rounding,
                    )
                    <= 0
                ):
                    procure_method = "make_to_stock"
                    forecasted_qties_by_loc[rule.location_src_id][
                        procurement.product_id.id
                    ] -= qty_needed
                else:
                    procure_method = "make_to_order"

            move_values = rule._get_stock_move_values(*procurement)
            move_values["procure_method"] = procure_method
            moves_values_by_company[procurement.company_id.id].append(move_values)

        for company_id, moves_values in moves_values_by_company.items():
            # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            moves = (
                self.env["stock.move"]
                .with_user(SUPERUSER_ID)
                .sudo()
                .with_company(company_id)
                .create(moves_values)
            )
            # Since action_confirm launch following procurement_group we should activate it.
            moves._action_confirm()
        return True

    @api.model
    def _run_pull(self, procurements):
        product_template_procurements = []
        product_procurements = []
        for procurement, rule in procurements:
            if isinstance(
                procurement.product_id, self.env["product.product"].__class__
            ):
                product_procurements.append((procurement, rule))
            else:
                product_template_procurements.append((procurement, rule))

        super()._run_pull(product_procurements)
        self._run_pull_product_template(product_template_procurements)
        return True

    def _get_stock_move_values(self, product, *args):
        """Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'pull' or 'pull_push') set on it.

        :param procurement: browse record
        :rtype: dictionary
        """
        stock_move_data = super()._get_stock_move_values(product, *args)
        if not isinstance(product, self.env["product.product"].__class__):
            stock_move_data["product_template_id"] = stock_move_data.pop("product_id")
        return stock_move_data
