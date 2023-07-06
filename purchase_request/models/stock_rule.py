# Copyright 2018-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _prepare_purchase_request_line(self, request_id, procurement):
        procurement_uom_po_qty = procurement.product_uom._compute_quantity(
            procurement.product_qty, procurement.product_id.uom_po_id
        )
        return {
            "product_id": procurement.product_id.id,
            "name": procurement.product_id.name,
            "date_required": "date_planned" in procurement.values
            and procurement.values["date_planned"]
            or fields.Datetime.now(),
            "product_uom_id": procurement.product_id.uom_po_id.id,
            "product_qty": procurement_uom_po_qty,
            "request_id": request_id.id,
            "move_dest_ids": [
                (4, x.id) for x in procurement.values.get("move_dest_ids", [])
            ],
            "orderpoint_id": procurement.values.get("orderpoint_id", False)
            and procurement.values.get("orderpoint_id").id,
        }

    @api.model
    def _prepare_purchase_request(self, origin, values):
        gpo = self.group_propagation_option
        group_id = (
            (gpo == "fixed" and self.group_id.id)
            or (gpo == "propagate" and values.get("group_id") and values["group_id"].id)
            or False
        )
        return {
            "origin": origin,
            "company_id": values["company_id"].id,
            "picking_type_id": self.picking_type_id.id,
            "group_id": group_id or False,
        }

    @api.model
    def _make_pr_get_domain(self, values):
        """
        This method is to be implemented by other modules that can
        provide a criteria to select the appropriate purchase request to be
        extended.
        :return: False
        """
        domain = (
            ("state", "=", "draft"),
            ("picking_type_id", "=", self.picking_type_id.id),
            ("company_id", "=", values["company_id"].id),
        )
        gpo = self.group_propagation_option
        group_id = (
            (gpo == "fixed" and self.group_id.id)
            or (gpo == "propagate" and values["group_id"].id)
            or False
        )
        if group_id:
            domain += (("group_id", "=", group_id),)
        return domain

    def is_create_purchase_request_allowed(self, procurement):
        """
        Tell if current procurement order should
        create a purchase request or not.
        :return: boolean
        """
        return (
            procurement[1].action == "buy"
            and procurement[0].product_id.purchase_request
        )

    def _run_buy(self, procurements):
        indexes_to_pop = []
        for i, procurement in enumerate(procurements):
            if self.is_create_purchase_request_allowed(procurement):
                self.create_purchase_request(procurement)
                indexes_to_pop.append(i)
        if indexes_to_pop:
            indexes_to_pop.reverse()
            for index in indexes_to_pop:
                procurements.pop(index)
        if not procurements:
            return
        return super(StockRule, self)._run_buy(procurements)

    def create_purchase_request(self, procurement_group):
        """
        Create a purchase request containing procurement order product.
        """
        procurement = procurement_group[0]
        rule = procurement_group[1]
        purchase_request_model = self.env["purchase.request"]
        purchase_request_line_model = self.env["purchase.request.line"]
        cache = {}
        pr = self.env["purchase.request"]
        domain = rule._make_pr_get_domain(procurement.values)
        if domain in cache:
            pr = cache[domain]
        elif domain:
            pr = self.env["purchase.request"].search([dom for dom in domain])
            pr = pr[0] if pr else False
            cache[domain] = pr
        if not pr:
            request_data = rule._prepare_purchase_request(
                procurement.origin, procurement.values
            )
            pr = purchase_request_model.create(request_data)
            cache[domain] = pr
        elif (
            not pr.origin
            or procurement.origin not in pr.origin.split(", ")
            and procurement.origin != "/"
        ):
            if pr.origin:
                if procurement.origin:
                    pr.write({"origin": pr.origin + ", " + procurement.origin})
            else:
                pr.write({"origin": procurement.origin})
        # Create Line
        request_line_data = rule._prepare_purchase_request_line(pr, procurement)
        purchase_request_line_model.create(request_line_data)
