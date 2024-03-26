from odoo.tests import SavepointCase


class ReserveRuleCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(ReserveRuleCommon, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_delta = cls.env.ref("base.res_partner_4")
        cls.wh = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WHTEST",
            }
        )
        cls.rule = cls.env.ref("stock_reserve_rule.stock_reserve_rule_1_demo")
        cls.rule.active = True

        cls.customer_loc = cls.env.ref("stock.stock_location_customers")

        cls.loc_zone1 = cls.env["stock.location"].create(
            {"name": "Zone1", "location_id": cls.wh.lot_stock_id.id}
        )
        cls.loc_zone1_bin1 = cls.env["stock.location"].create(
            {"name": "Zone1 Bin1", "location_id": cls.loc_zone1.id}
        )
        cls.loc_zone1_bin2 = cls.env["stock.location"].create(
            {"name": "Zone1 Bin2", "location_id": cls.loc_zone1.id}
        )
        cls.loc_zone2 = cls.env["stock.location"].create(
            {"name": "Zone2", "location_id": cls.wh.lot_stock_id.id}
        )
        cls.loc_zone2_bin1 = cls.env["stock.location"].create(
            {"name": "Zone2 Bin1", "location_id": cls.loc_zone2.id}
        )
        cls.loc_zone2_bin2 = cls.env["stock.location"].create(
            {"name": "Zone2 Bin2", "location_id": cls.loc_zone2.id}
        )
        cls.loc_zone3 = cls.env["stock.location"].create(
            {"name": "Zone3", "location_id": cls.wh.lot_stock_id.id}
        )
        cls.loc_zone3_bin1 = cls.env["stock.location"].create(
            {"name": "Zone3 Bin1", "location_id": cls.loc_zone3.id}
        )
        cls.loc_zone3_bin2 = cls.env["stock.location"].create(
            {"name": "Zone3 Bin2", "location_id": cls.loc_zone3.id}
        )
        cls.loc_zone4 = cls.env["stock.location"].create(
            {"name": "Zone4", "location_id": cls.wh.lot_stock_id.id}
        )
        cls.loc_zone4_bin1 = cls.env["stock.location"].create(
            {"name": "Zone4 Bin1", "location_id": cls.loc_zone4.id}
        )
        cls.loc_zone4_bin2 = cls.env["stock.location"].create(
            {"name": "Zone4 Bin2", "location_id": cls.loc_zone4.id}
        )

        cls.product1 = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "Product 2", "type": "product"}
        )
        cls.product3 = cls.env["product.product"].create(
            {"name": "Product 3", "type": "product", "tracking": "lot"}
        )

        cls.unit = cls.env["product.packaging.type"].create(
            {"name": "Unit", "code": "UNIT", "sequence": 0}
        )
        cls.retail_box = cls.env["product.packaging.type"].create(
            {"name": "Retail Box", "code": "PACK", "sequence": 3}
        )
        cls.transport_box = cls.env["product.packaging.type"].create(
            {"name": "Transport Box", "code": "CASE", "sequence": 4}
        )
        cls.pallet = cls.env["product.packaging.type"].create(
            {"name": "Pallet", "code": "PALLET", "sequence": 5}
        )
        cls.lot0_id = cls.env["stock.production.lot"].create(
            {"name": "0101", "product_id": cls.product3.id}
        )
        cls.lot1_id = cls.env["stock.production.lot"].create(
            {"name": "0102", "product_id": cls.product3.id}
        )

    def _create_picking(
        self, wh, products=None, location_src_id=None, picking_type_id=None
    ):
        """Create picking

        Products must be a list of tuples (product, quantity).
        One stock move will be created for each tuple.
        """
        if products is None:
            products = []

        picking = self.env["stock.picking"].create(
            {
                "location_id": location_src_id or wh.lot_stock_id.id,
                "location_dest_id": wh.wh_output_stock_loc_id.id,
                "partner_id": self.partner_delta.id,
                "picking_type_id": picking_type_id or wh.pick_type_id.id,
            }
        )

        for product, qty in products:
            self.env["stock.move"].create(
                {
                    "name": product.name,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "product_uom": product.uom_id.id,
                    "picking_id": picking.id,
                    "location_id": location_src_id or wh.lot_stock_id.id,
                    "location_dest_id": wh.wh_output_stock_loc_id.id,
                    "state": "confirmed",
                }
            )
        return picking

    def _update_qty_in_location(
        self, location, product, quantity, in_date=None, lot_id=None, owner_id=None
    ):
        self.env["stock.quant"]._update_available_quantity(
            product,
            location,
            quantity,
            in_date=in_date,
            lot_id=lot_id,
            owner_id=owner_id,
        )

    def _create_rule(self, rule_values, removal_values):
        rule_config = {
            "name": "Test Rule",
            "location_id": self.wh.lot_stock_id.id,
            "rule_removal_ids": [(0, 0, values) for values in removal_values],
        }
        rule_config.update(rule_values)
        record = self.env["stock.reserve.rule"].create(rule_config)
        # workaround for https://github.com/odoo/odoo/pull/41900
        self.env["stock.reserve.rule"].invalidate_cache()
        return record

    def _setup_packagings(self, product, packagings):
        """Create packagings on a product
        packagings is a list [(name, qty, packaging_type)]
        """
        self.env["product.packaging"].create(
            [
                {
                    "name": name,
                    "qty": qty,
                    "product_id": product.id,
                    "packaging_type_id": packaging_type.id,
                }
                for name, qty, packaging_type in packagings
            ]
        )
