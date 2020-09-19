# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.osv import expression
from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def _get_domain_locations_new(
            self, location_ids, company_id=False, compute_child=True):
        """
        This is used to exclude locations if needed
        :param location_ids:
        :param company_id:
        :param compute_child:
        :return:
        """
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = super(
            ProductProduct, self)._get_domain_locations_new(
            location_ids=location_ids,
            company_id=company_id,
            compute_child=compute_child)
        excluded_location_ids = self.env.context.get("excluded_location_ids")
        if excluded_location_ids:
            domain_quant_loc = expression.AND([
                [("location_id", "not in", excluded_location_ids.ids)],
                domain_quant_loc,
            ])
            domain_move_in_loc = expression.AND([
                [("location_dest_id", "not in", excluded_location_ids.ids)],
                domain_quant_loc,
            ])
            domain_move_out_loc = expression.AND([
                [("location_id", "not in", excluded_location_ids.ids)],
                domain_quant_loc,
            ])
        return domain_quant_loc, domain_move_in_loc, domain_move_out_loc
