from odoo.tests import SavepointCase


class TestCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        Product = cls.env["product.product"]
        ProcurementGroup = cls.env["procurement.group"]
        StockLocationRoute = cls.env["stock.location.route"]
        StockRule = cls.env["stock.rule"]
        StockQuant = cls.env["stock.quant"]

        cls.warehouse = cls.env.ref("stock.warehouse0")

        route_mto_mts = cls.env.ref("stock_mts_mto_rule.route_mto_mts")

        location_stock_id = cls.env.ref("stock.stock_location_stock").id

        dummy_route = StockLocationRoute.create(
            {
                "name": "dummy route",
                "warehouse_selectable": True,
            }
        )

        cls.warehouse.write(
            {"route_ids": [(4, dummy_route.id)], "mto_mts_management": True}
        )

        cls.product = Product.create(
            {
                "name": "Test Product",
                "type": "product",
                "route_ids": [(6, 0, route_mto_mts.ids)],
            }
        )

        cls.group = ProcurementGroup.create({"name": "test"})
        cls.dummy_rule = StockRule.create(
            {
                "name": "dummy rule",
                "location_id": location_stock_id,
                "location_src_id": cls.env.ref("stock.stock_location_suppliers").id,
                "action": "pull",
                "warehouse_id": cls.warehouse.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "route_id": dummy_route.id,
            }
        )

        cls.quant = StockQuant.create(
            {
                "owner_id": cls.env.ref("base.main_partner").id,
                "location_id": location_stock_id,
                "product_id": cls.product.id,
                "quantity": 3,
            }
        )

    def run_procurement_group_and_get_stock_move(self, qty):
        self.env["procurement.group"].run(
            [
                self.group.Procurement(
                    self.product,
                    qty,
                    self.env.ref("uom.product_uom_unit"),
                    self.env.ref("stock.stock_location_customers"),
                    self.product.name,
                    "test",
                    self.warehouse.company_id,
                    {"warehouse_id": self.warehouse, "group_id": self.group},
                )
            ]
        )
        return self.env["stock.move"].search([("group_id", "=", self.group.id)])
