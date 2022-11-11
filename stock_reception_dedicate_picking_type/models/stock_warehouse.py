# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    stock_in_type_id = fields.Many2one(
        "stock.picking.type", string="Stock In Operation Type"
    )

    quality_type_id = fields.Many2one(
        "stock.picking.type", string="Quality Check Operation Type"
    )

    def _get_picking_type_update_values(self):
        data = super()._get_picking_type_update_values()
        data.update(
            {
                "stock_in_type_id": {
                    "default_location_dest_id": self.lot_stock_id.id,
                    "active": self.reception_steps != "one_step" and self.active,
                },
                "quality_type_id": {
                    "default_location_dest_id": self.lot_stock_id.id,
                    "active": self.reception_steps == "three_steps" and self.active,
                },
            }
        )
        return data

    def _get_picking_type_create_values(self, max_sequence):
        data, max_sequence = super()._get_picking_type_create_values(max_sequence)
        data.update(
            {
                "stock_in_type_id": {
                    "name": _("Stock In"),
                    "code": "internal",
                    "default_location_src_id": self.wh_input_stock_loc_id.id,
                    "default_location_dest_id": self.lot_stock_id.id,
                    "sequence": max_sequence + 1,
                    "sequence_code": "STOCKIN",
                    "company_id": self.company_id.id,
                },
                "quality_type_id": {
                    "name": _("Quality Check"),
                    "code": "internal",
                    "default_location_src_id": self.wh_input_stock_loc_id.id,
                    "default_location_dest_id": self.lot_stock_id.id,
                    "sequence": max_sequence + 2,
                    "sequence_code": "CHECK",
                    "company_id": self.company_id.id,
                },
            }
        )
        return data, max_sequence + 3

    def get_rules_dict(self):
        result = super().get_rules_dict()
        customer_loc, supplier_loc = self._get_partner_locations()
        for warehouse in self:
            result[warehouse.id].update(
                {
                    "two_steps": [
                        self.Routing(
                            supplier_loc,
                            warehouse.wh_input_stock_loc_id,
                            warehouse.in_type_id,
                            "pull",
                        ),
                        self.Routing(
                            warehouse.wh_input_stock_loc_id,
                            warehouse.lot_stock_id,
                            warehouse.stock_in_type_id,
                            "pull_push",
                        ),
                    ],
                    "three_steps": [
                        self.Routing(
                            supplier_loc,
                            warehouse.wh_input_stock_loc_id,
                            warehouse.in_type_id,
                            "pull",
                        ),
                        self.Routing(
                            warehouse.wh_input_stock_loc_id,
                            warehouse.wh_qc_stock_loc_id,
                            warehouse.quality_type_id,
                            "pull_push",
                        ),
                        self.Routing(
                            warehouse.wh_qc_stock_loc_id,
                            warehouse.lot_stock_id,
                            warehouse.quality_type_id,
                            "pull_push",
                        ),
                    ],
                }
            )
            result[warehouse.id].update(warehouse._get_receive_rules_dict())
        return result

    def _get_sequence_values(self):
        values = super()._get_sequence_values()
        values.update(
            {
                "stock_in_type_id": {
                    "name": self.name + " " + _("Sequence Stock In"),
                    "prefix": self.code + "/STOCKIN/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
                "quality_type_id": {
                    "name": self.name + " " + _("Sequence Quality Check"),
                    "prefix": self.code + "/QUALITY/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
            }
        )
        return values

    def _get_receive_rules_dict(self):
        result = super()._get_receive_rules_dict()
        result["two_steps"] = [
            self.Routing(
                self.wh_input_stock_loc_id,
                self.lot_stock_id,
                self.stock_in_type_id,
                "pull_push",
            )
        ]
        result["three_steps"] = [
            self.Routing(
                self.wh_input_stock_loc_id,
                self.wh_qc_stock_loc_id,
                self.quality_type_id,
                "pull_push",
            ),
            self.Routing(
                self.wh_qc_stock_loc_id,
                self.lot_stock_id,
                self.quality_type_id,
                "pull_push",
            ),
        ]
        return result

    def _create_or_update_sequences_and_picking_types(self):
        data = super()._create_or_update_sequences_and_picking_types()
        stock_picking_type = self.env["stock.picking.type"]
        if "stock_in_type_id" in data:
            stock_picking_type.browse(data["stock_in_type_id"]).write(
                {"return_picking_type_id": data.get("stock_in_type_id", False)}
            )
        if "quality_type_id" in data:
            stock_picking_type.browse(data["quality_type_id"]).write(
                {"return_picking_type_id": data.get("quality_type_id", False)}
            )
        return data

    @api.model
    def _create_missing_picking_types(self):
        warehouses = self.env["stock.warehouse"].search(
            ["|", ("stock_in_type_id", "=", False), ("quality_type_id", "=", False)]
        )
        for warehouse in warehouses:
            new_vals = warehouse._create_or_update_sequences_and_picking_types()
            warehouse.write(new_vals)
