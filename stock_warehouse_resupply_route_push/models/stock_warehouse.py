# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import Command, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    resupply_wh_push = fields.Boolean(
        string="Resupply from another Warehouse with Push Rules",
        help="Note that this will create new operation type for "
        "inter-warehouse deliveries.",
        default=False,
    )
    out_inter_wh_internal_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Inter Warehouse (internal) Type",
        check_company=True,
        copy=False,
    )
    out_inter_wh_external_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Inter Warehouse (external) Type",
        check_company=True,
        copy=False,
    )

    def _get_picking_type_create_values(self, max_sequence):
        values, max_sequence = super()._get_picking_type_create_values(max_sequence)
        values.update(
            {
                "out_inter_wh_internal_type_id": {
                    "name": _("Delivery Orders (Inter Warehouse)"),
                    "code": "outgoing",
                    "use_create_lots": False,
                    "sequence": max_sequence + 2,
                    "sequence_code": "IW",
                    "print_label": True,
                    "company_id": self.company_id.id,
                },
                "out_inter_wh_external_type_id": {
                    "name": _("Delivery Orders (Inter Warehouse - External)"),
                    "code": "outgoing",
                    "use_create_lots": False,
                    "sequence": max_sequence + 3,
                    "sequence_code": "IWE",
                    "print_label": True,
                    "company_id": self.company_id.id,
                },
            }
        )
        return values, max_sequence + 4

    def _get_sequence_values(self, name=False, code=False):
        values = super()._get_sequence_values(name=name, code=code)
        name = name if name else self.name
        code = code if code else self.code
        values.update(
            {
                "out_inter_wh_internal_type_id": {
                    "name": _("%(name)s Sequence inter warehouse", name=name),
                    "prefix": code
                    + "/"
                    + (self.out_inter_wh_internal_type_id.sequence_code or "IW")
                    + "/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
                "out_inter_wh_external_type_id": {
                    "name": _(
                        "%(name)s Sequence inter warehouse (external)", name=name
                    ),
                    "prefix": code
                    + "/"
                    + (self.out_inter_wh_external_type_id.sequence_code or "IWE")
                    + "/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
            }
        )
        return values

    def _get_picking_type_update_values(self):
        values = super()._get_picking_type_update_values()
        input_loc, output_loc = self._get_input_output_locations(
            self.reception_steps, self.delivery_steps
        )
        internal_transit_location, external_transit_location = (
            self._get_transit_locations()
        )
        values.update(
            {
                "out_inter_wh_internal_type_id": {
                    "default_location_src_id": output_loc.id,
                    "default_location_dest_id": internal_transit_location.id,
                    "barcode": self.code.replace(" ", "").upper() + "IW",
                },
                "out_inter_wh_external_type_id": {
                    "default_location_src_id": output_loc.id,
                    "default_location_dest_id": external_transit_location.id,
                    "barcode": self.code.replace(" ", "").upper() + "IWE",
                },
            }
        )
        return values

    def _is_internal_inter_wh(self, supplier_wh):
        return supplier_wh.company_id == self.company_id

    def create_resupply_routes(self, supplier_warehouses):
        if not self.resupply_wh_push:
            return super().create_resupply_routes(supplier_warehouses)
        if not self.partner_id:
            raise ValidationError(
                _(
                    "Address is required in warehouse %s to use "
                    "Inter-warehouse push routes generation."
                )
                % self.name
            )
        # For now, it is still not possible to use push for inter-warehouses
        # between 2 companies, because we cannot create a stock rule with
        # locations of different companies.
        same_company_whs = supplier_warehouses.filtered(
            lambda wh: wh.company_id == self.company_id
        )
        res = super().create_resupply_routes(supplier_warehouses - same_company_whs)
        Route = self.env["stock.route"]
        Rule = self.env["stock.rule"]
        internal_transit_location, external_transit_location = (
            self._get_transit_locations()
        )
        for supplier_wh in same_company_whs:
            transit_location = (
                internal_transit_location
                if self._is_internal_inter_wh(supplier_wh)
                else external_transit_location
            )
            if (
                not supplier_wh.out_inter_wh_internal_type_id
                or not supplier_wh.out_inter_wh_external_type_id
            ):
                new_vals = supplier_wh._create_or_update_sequences_and_picking_types()
                supplier_wh.write(new_vals)
            supplier_wh_picking_type = (
                supplier_wh.out_inter_wh_internal_type_id
                if self._is_internal_inter_wh(supplier_wh)
                else supplier_wh.out_inter_wh_external_type_id
            )
            if not transit_location:
                continue
            transit_location.active = True
            output_location = (
                supplier_wh.lot_stock_id
                if supplier_wh.delivery_steps == "ship_only"
                else supplier_wh.wh_output_stock_loc_id
            )

            inter_wh_route = Route.create(
                self._get_inter_warehouse_route_values(supplier_wh)
            )
            rules_list = supplier_wh._get_supply_pull_rules_values(
                [
                    self.Routing(
                        output_location,
                        self.lot_stock_id,
                        supplier_wh_picking_type,
                        "pull",
                    )
                ],
                values={
                    "route_id": inter_wh_route.id,
                    "location_dest_from_rule": False,
                    "warehouse_id": self.id,
                    "partner_address_id": self.partner_id.id,
                },
            )
            if supplier_wh.delivery_steps != "ship_only":
                # Replenish from Output location
                # we need to force warehouse_id to null to overcome the fact that we
                # cannot propagate to a different warehouse when procuring from a
                # location already in a defined warehouse (i.e. the WH/output
                # location).
                # https://github.com/odoo/odoo/blob/581e04c4fa9dd84a669ea48154c0def81e9c7311/addons/stock/models/stock_move.py#L1651
                rules_list += supplier_wh._get_supply_pull_rules_values(
                    [
                        self.Routing(
                            supplier_wh.lot_stock_id,
                            output_location,
                            supplier_wh.pick_type_id,
                            "pull",
                        )
                    ],
                    values={
                        "route_id": inter_wh_route.id,
                        "warehouse_id": False,
                        "location_dest_from_rule": True,
                    },
                )
            rules_list += self._get_rule_values(
                [
                    self.Routing(
                        transit_location, self.lot_stock_id, self.in_type_id, "push"
                    )
                ],
                values={
                    "warehouse_id": False,
                    "route_id": inter_wh_route.id,
                    "propagate_warehouse_id": supplier_wh.id,
                    "push_domain": "[('partner_id', '=', %d)]" % self.partner_id.id,
                },
            )
            for rule_vals in rules_list:
                Rule.create(rule_vals)
        return res

    def action_recreate_resupply_routes(self):
        for rec in self:
            old_route_assigments = {}
            for old_route in rec.resupply_route_ids:
                old_route_assigments[old_route.supplier_wh_id] = {
                    "product_ids": old_route.product_ids.ids,
                    "categ_ids": old_route.categ_ids.ids,
                    "warehouse_ids": old_route.warehouse_ids.ids,
                }
                old_route.active = False
                old_route.rule_ids.write({"active": False})
                old_route.name = (
                    f"{old_route.name} - Deprecated on {fields.Date.today()}"
                )
            rec.resupply_route_ids = [Command.clear()]
            rec.create_resupply_routes(rec.resupply_wh_ids)
            # reassign old route assignments:
            for new_route in rec.resupply_route_ids:
                old_assignment = old_route_assigments.get(new_route.supplier_wh_id)
                if old_assignment:
                    new_route.write(old_assignment)
        return True
