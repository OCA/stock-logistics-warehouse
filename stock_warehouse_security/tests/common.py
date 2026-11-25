from decorator import decorator

from odoo.tests.common import Form, SavepointCase


def allowed_companies():
    """Decorate a method to change allowed companies in current
    context from current user info.

    This is to mimic user interface as if current user has choosen
    all allowed companies from the list of available companies he can
    currently see.

    you should probably associate it with the @users decorator.
    Ordering your decorator is important otherwise you won't get proper list
    of companies.

    @users(
        "user1",
    )
    @allowed_companies()
    def test_something(self):
        # return data will be filtered by allowed user1 companies
        self.env["some.model"].search([])
    """

    @decorator
    def wrapper(func, *args, **kwargs):
        self = args[0]

        previous_allowed_company_ids = self.env.context.get("allowed_company_ids")
        try:
            self.env = self.env(
                context=dict(
                    self.env.context,
                    # company_id=self.env.user.company_ids[0].id,
                    allowed_company_ids=self.env.user.company_ids.ids,
                )
            )
            func(*args, **kwargs)
        finally:
            self.env = self.env(
                context=dict(
                    self.env.context,
                    allowed_company_ids=previous_allowed_company_ids,
                )
            )

    return wrapper


class TestStockCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company_1 = cls.env.ref("base.main_company")
        cls.company_2 = cls.env["res.company"].create({"name": "company 2"})
        cls.warehouse_0 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 1",
                "company_id": cls.company_1.id,
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WH1",
            }
        )
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 2",
                "company_id": cls.company_1.id,
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WH2",
            }
        )
        cls.warehouse_3 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 3 - company 2",
                "company_id": cls.company_2.id,
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WH3",
            }
        )
        cls.warehouses = cls.warehouse_1 | cls.warehouse_2 | cls.warehouse_3
        cls.suppliers_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")

        cls.stock_user_c1_wh12 = cls.env["res.users"].create(
            {
                "name": "unlimited multi warehouse user",
                "login": "stock_user_c1_wh12",
                "groups_id": [(6, 0, [cls.env.ref("stock.group_stock_user").id])],
                "warehouse_ids": [],
                "company_ids": [(6, 0, cls.company_1.ids)],
            }
        )
        cls.stock_user_c12_wh2 = cls.env["res.users"].create(
            {
                "name": "Limited warehouse user",
                "login": "stock_user_c12_wh2",
                "groups_id": [(6, 0, [cls.env.ref("stock.group_stock_user").id])],
                "warehouse_ids": [(6, 0, cls.warehouse_2.ids)],
                "company_ids": [(6, 0, (cls.company_1 | cls.company_2).ids)],
            }
        )
        cls.stock_user_c12_wh23 = cls.env["res.users"].create(
            {
                "name": "Limited warehouse user",
                "login": "stock_user_c12_wh23",
                "groups_id": [(6, 0, [cls.env.ref("stock.group_stock_user").id])],
                "warehouse_ids": [(6, 0, (cls.warehouse_2 | cls.warehouse_3).ids)],
                "company_ids": [(6, 0, (cls.company_1 | cls.company_2).ids)],
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product for test",
                "type": "product",
            }
        )
        cls.stock_picking_wh_1 = cls._create_picking(
            cls.warehouse_1, location_src=cls.suppliers_location
        )
        cls.stock_picking_wh_2 = cls._create_picking(
            cls.warehouse_2, location_src=cls.suppliers_location
        )
        cls.stock_picking_wh_3 = cls._create_picking(
            cls.warehouse_3, location_src=cls.suppliers_location
        )
        cls.stock_pickings = (
            cls.stock_picking_wh_1 | cls.stock_picking_wh_2 | cls.stock_picking_wh_3
        )
        cls.stock_pickings.action_confirm()
        cls.stock_pickings.action_assign()
        for wh in cls.warehouses:
            cls.env["stock.warehouse.orderpoint"].with_company(wh.company_id).create(
                {
                    "name": f"RR for {wh.name}",
                    "warehouse_id": wh.id,
                    "location_id": wh.lot_stock_id.id,
                    "product_id": cls.product.id,
                    "product_min_qty": 1,
                    "product_max_qty": 5,
                }
            )

    @classmethod
    def _create_picking(
        cls,
        warehouse,
        picking_type=None,
        location_src=None,
        location_dest=None,
        env=None,
    ):
        if not picking_type:
            picking_type = warehouse.in_type_id

        if not location_src:
            location_src = picking_type.default_location_src_id

        if not location_dest:
            location_dest = picking_type.default_location_dest_id

        if not env:
            env = cls.env

        location_src.ensure_one()
        location_dest.ensure_one()

        picking_form = Form(env["stock.picking"].with_company(warehouse.company_id))
        picking_form.picking_type_id = picking_type
        picking_form.location_id = location_src
        picking_form.location_dest_id = location_dest
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.product
            move.product_uom_qty = 5
            move.location_id = location_src
            move.location_dest_id = location_dest
        return picking_form.save()
