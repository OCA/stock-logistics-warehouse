# -*- coding: utf-8 -*-

from odoo import models


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False, index=0, product_info=False, ignore_stock=False):
        res = super()._get_bom_data(bom, warehouse, product, line_qty, bom_line, level, parent_bom, index, product_info, ignore_stock)
        operations = res.get('operations', False)
        if "operations":
            for operation in operations:
                pcost = operation.get('operation').workcenter_id.analytic_product_id.proposed_cost
                operation["proposed_cost"] = pcost
        res["proposed_cost"] = res["product"].proposed_cost * res["quantity"]
        return res

    def _get_component_data(self, bom, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock=False):
        res = super()._get_component_data(bom, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock)
        res["proposed_cost"] = res["product"].proposed_cost * res["quantity"]
        return res

    def _get_bom_array_lines(self, data, level, unfolded_ids, unfolded, parent_unfolded):
        lines = super()._get_bom_array_lines(data, level, unfolded_ids, unfolded, parent_unfolded)
        for component in data.get('components', []):
            if not component['bom_id']:
                bom_line = next(filter(lambda l: l.get('name', None) == component['name'], lines))
                if bom_line:
                    bom_line['proposed_cost'] = component['proposed_cost']
        return lines
