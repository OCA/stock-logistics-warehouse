from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

READONLY_STATES = {
    "draft": [("readonly", False)],
}


class InventoryAdjustmentsGroup(models.Model):
    _name = "stock.inventory"
    _description = "Inventory Adjustment Group"
    _order = "date desc, id desc"
    _inherit = [
        "mail.thread",
    ]

    name = fields.Char(
        required=True,
        default="Inventory",
        string="Inventory Reference",
        readonly=True,
        states=READONLY_STATES,
    )

    date = fields.Datetime(
        default=lambda self: fields.Datetime.now(),
        readonly=True,
        states=READONLY_STATES,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        readonly=True,
        index=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.company,
        required=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )

    owner_id = fields.Many2one(
        "res.partner",
        "Owner",
        help="This is the owner of the inventory adjustment",
        readonly=True,
        states=READONLY_STATES,
    )

    location_ids = fields.Many2many(
        "stock.location",
        string="Locations",
        domain="[('usage', '=', 'internal'), "
        "'|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        readonly=True,
        states=READONLY_STATES,
    )

    product_selection = fields.Selection(
        [
            ("all", "All Products"),
            ("manual", "Manual Selection"),
            ("category", "Product Category"),
            ("one", "One Product"),
            ("lot", "Lot/Serial Number"),
        ],
        default="all",
        required=True,
        readonly=True,
        states=READONLY_STATES,
    )

    product_ids = fields.Many2many(
        "product.product",
        string="Products",
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        readonly=True,
        states=READONLY_STATES,
    )

    stock_quant_ids = fields.Many2many(
        "stock.quant",
        string="Inventory Adjustment",
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        readonly=True,
        states=READONLY_STATES,
    )

    category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        readonly=True,
        states=READONLY_STATES,
    )

    lot_ids = fields.Many2many(
        "stock.lot",
        string="Lot/Serial Numbers",
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        readonly=True,
        states=READONLY_STATES,
    )

    stock_move_ids = fields.One2many(
        "stock.move.line",
        "inventory_adjustment_id",
        string="Inventory Adjustments Done",
        readonly=True,
        states=READONLY_STATES,
    )

    count_stock_quants = fields.Integer(
        compute="_compute_count_stock_quants", string="# Adjustments"
    )

    count_stock_quants_string = fields.Char(
        compute="_compute_count_stock_quants", string="Adjustments"
    )

    count_stock_moves = fields.Integer(
        compute="_compute_count_stock_moves", string="Stock Moves Lines"
    )
    action_state_to_cancel_allowed = fields.Boolean(
        compute="_compute_action_state_to_cancel_allowed"
    )

    exclude_sublocation = fields.Boolean(
        help="If enabled, it will only take into account "
        "the locations selected, and not their children."
    )

    responsible_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        states={"draft": [("readonly", False)]},
        readonly=True,
        help="Specific responsible of Inventory Adjustment.",
    )

    products_under_review_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_products_under_review_ids",
        search="_search_products_under_review_ids",
        string="Products Under Review",
        relation="stock_inventory_product_review_rel",
    )

    auto_create_missing_quants = fields.Boolean(
        string="Create missing quants",
        readonly=True,
        states=READONLY_STATES,
        default=False,
    )

    def _search_products_under_review_ids(self, operator, value):
        quants = self.env["stock.quant"].search(
            [("to_do", "=", True), ("product_id", operator, value)]
        )
        inventories = quants.mapped("stock_inventory_ids")
        return [("id", "in", inventories.ids), ("state", "=", "in_progress")]

    @api.depends("stock_quant_ids", "stock_quant_ids.to_do", "state")
    def _compute_products_under_review_ids(self):
        for record in self:
            if record.state == "in_progress":
                products = record.stock_quant_ids.filtered(
                    lambda quant: quant.to_do
                ).mapped("product_id")
                record.products_under_review_ids = (
                    [(6, 0, products.ids)] if products else [(5, 0, 0)]
                )
            else:
                record.products_under_review_ids = [(5, 0, 0)]

    @api.depends("stock_quant_ids")
    def _compute_count_stock_quants(self):
        for rec in self:
            quants = rec.stock_quant_ids
            quants_to_do = quants.filtered(lambda q: q.to_do)
            count_todo = len(quants_to_do)
            rec.count_stock_quants = len(quants)
            rec.count_stock_quants_string = "{} / {}".format(
                count_todo, rec.count_stock_quants
            )

    @api.depends("stock_move_ids")
    def _compute_count_stock_moves(self):
        group_fname = "inventory_adjustment_id"
        group_data = self.env["stock.move.line"].read_group(
            [
                (group_fname, "in", self.ids),
            ],
            [group_fname],
            [group_fname],
        )
        data_by_adj_id = {
            row[group_fname][0]: row.get(f"{group_fname}_count", 0)
            for row in group_data
        }
        for rec in self:
            rec.count_stock_moves = data_by_adj_id.get(rec.id, 0)

    def _compute_action_state_to_cancel_allowed(self):
        for rec in self:
            rec.action_state_to_cancel_allowed = rec.state == "draft"

    @api.onchange("company_id")
    def _onchange_load_auto_create_missing_quants(self):
        for rec in self:
            rec.auto_create_missing_quants = (
                rec.company_id.stock_inventory_auto_create_missing_quants
            )

    def _get_quants(self, locations):
        self.ensure_one()
        domain = []
        base_domain = self._get_base_domain(locations)
        if self.product_selection == "all":
            domain = self._get_domain_all_quants(base_domain)
        elif self.product_selection == "manual":
            domain = self._get_domain_manual_quants(base_domain)
        elif self.product_selection == "one":
            domain = self._get_domain_one_quant(base_domain)
        elif self.product_selection == "lot":
            domain = self._get_domain_lot_quants(base_domain)
        elif self.product_selection == "category":
            domain = self._get_domain_category_quants(base_domain)
        return self.env["stock.quant"].search(domain)

    def _get_or_create_quants(self):
        """
        Create or retrieve stock.quant for the given inventory configuration
        :return: stock.quant
        """
        self.ensure_one()
        quant_ids = []
        for quant_values in self._get_quants_values():
            quant = self._get_quant(quant_values)
            quant_ids.append(quant.id)
        return self.env["stock.quant"].browse(quant_ids)

    def _get_quant(self, quant_values):
        """
        Get an existing or create a new quant based on preloaded quant values
        product_id, lot_id and location_id must be present.
        :param quant_values:
        :return:
        """
        self.ensure_one()
        Quant = self.env["stock.quant"]

        quant = Quant.search(
            [
                ("product_id", "=", quant_values.get("product_id")),
                ("lot_id", "=", quant_values.get("lot_id")),
                ("location_id", "=", quant_values.get("location_id")),
            ],
            limit=1,
        )
        if not quant:
            quant = Quant.create(quant_values)
        return quant

    def _get_base_domain(self, locations):
        return (
            [
                ("location_id", "in", locations.mapped("id")),
            ]
            if self.exclude_sublocation
            else [
                ("location_id", "child_of", locations.child_internal_location_ids.ids),
            ]
        )

    def _get_domain_all_quants(self, base_domain):
        return base_domain

    def _get_domain_manual_quants(self, base_domain):
        self.ensure_one()
        return expression.AND(
            [base_domain, [("product_id", "in", self.product_ids.ids)]]
        )

    def _get_domain_one_quant(self, base_domain):
        self.ensure_one()
        return expression.AND(
            [
                base_domain,
                [
                    ("product_id", "in", self.product_ids.ids),
                ],
            ]
        )

    def _get_domain_lot_quants(self, base_domain):
        self.ensure_one()
        return expression.AND(
            [
                base_domain,
                [
                    ("product_id", "in", self.product_ids.ids),
                    ("lot_id", "in", self.lot_ids.ids),
                ],
            ]
        )

    def _get_domain_category_quants(self, base_domain):
        self.ensure_one()
        return expression.AND(
            [
                base_domain,
                [
                    "|",
                    ("product_id.categ_id", "=", self.category_id.id),
                    ("product_id.categ_id", "in", self.category_id.child_id.ids),
                ],
            ]
        )

    def refresh_stock_quant_ids(self):
        for rec in self:
            rec.stock_quant_ids = rec._get_quants(rec.location_ids)

    def _get_quant_joined_names(self, quants, field):
        return ", ".join(quants.mapped(f"{field}.display_name"))

    def _check_existing_in_progress_inventory(self):
        self.ensure_one()
        search_filter = [
            (
                "location_id",
                "child_of" if not self.exclude_sublocation else "in",
                self.location_ids.ids,
            ),
            ("to_do", "=", True),
        ]

        if self.product_ids:
            search_filter.append(("product_id", "in", self.product_ids.ids))
            error_field = "product_id"
            error_message = _(
                "There are active adjustments for the requested products: %(names)s. "
                "Blocking adjustments: %(blocking_names)s"
            )
        else:
            error_field = "location_id"
            error_message = _(
                "There's already an Adjustment in Process "
                "using one requested Location: %(names)s. "
                "Blocking adjustments: %(blocking_names)s"
            )

        quants = self.env["stock.quant"].search(search_filter)
        if quants:
            inventory_ids = self.env["stock.inventory"].search(
                [("stock_quant_ids", "in", quants.ids), ("state", "=", "in_progress")]
            )
            if inventory_ids:
                blocking_names = ", ".join(inventory_ids.mapped("name"))
                names = self._get_quant_joined_names(quants, error_field)
                raise ValidationError(
                    error_message % {"names": names, "blocking_names": blocking_names}
                )

    def action_state_to_in_progress(self):
        self.ensure_one()
        self._check_existing_in_progress_inventory()
        if self.auto_create_missing_quants:
            self._get_or_create_quants()
        quants = self._get_quants(self.location_ids)
        self.write(
            {
                "state": "in_progress",
                "stock_quant_ids": [(6, 0, quants.ids)],
            }
        )
        quants.write(
            {
                "to_do": True,
                "user_id": self.responsible_id.id or self.env.user.id,
                "inventory_date": self.date,
            }
        )
        return

    def action_state_to_done(self):
        self.ensure_one()
        self.state = "done"
        self.stock_quant_ids.update(
            {
                "to_do": False,
                "user_id": False,
                "inventory_date": False,
            }
        )
        return

    def action_auto_state_to_done(self):
        self.ensure_one()
        if not any(self.stock_quant_ids.filtered(lambda sq: sq.to_do)):
            self.action_state_to_done()
        return

    def action_state_to_draft(self):
        self.ensure_one()
        self.state = "draft"
        self.stock_quant_ids.update(
            {
                "to_do": False,
                "user_id": False,
                "inventory_date": False,
            }
        )
        self.stock_quant_ids = None
        return

    def action_state_to_cancel(self):
        self.ensure_one()
        self._check_action_state_to_cancel()
        self.write(
            {
                "state": "cancel",
            }
        )

    def _check_action_state_to_cancel(self):
        for rec in self:
            if not rec.action_state_to_cancel_allowed:
                raise UserError(
                    _(
                        "You can't cancel this inventory %(display_name)s.",
                        display_name=rec.display_name,
                    )
                )

    def action_view_inventory_adjustment(self):
        self.ensure_one()
        result = self.env["stock.quant"].action_view_inventory()
        context = result.get("context", {})
        context.update(
            {
                "search_default_to_do": 1,
                "inventory_id": self.id,
                "default_to_do": True,
                "default_user_id": self.env.user.id,
            }
        )
        result.update(
            {
                "domain": [("stock_inventory_ids", "in", self.ids)],
                "search_view_id": self.env.ref("stock.quant_search_view").id,
                "context": context,
            }
        )
        return result

    def action_view_stock_moves(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_inventory.action_view_stock_move_line_inventory_tree"
        )
        result["domain"] = [("inventory_adjustment_id", "=", self.id)]
        result["context"] = {}
        return result

    def _check_inventory_in_progress_not_override(self):
        for rec in self:
            if rec.state == "in_progress":
                location_condition = [
                    (
                        "location_ids",
                        "child_of" if not rec.exclude_sublocation else "in",
                        rec.location_ids.ids,
                    )
                ]
                if rec.product_ids:
                    product_condition = [
                        ("state", "=", "in_progress"),
                        ("id", "!=", rec.id),
                        ("product_ids", "in", rec.product_ids.ids),
                    ] + location_condition
                    inventories = self.search(product_condition)
                else:
                    inventories = self.search(
                        [("state", "=", "in_progress"), ("id", "!=", rec.id)]
                        + location_condition
                    )
                for inventory in inventories:
                    if any(
                        i in inventory.location_ids.ids for i in rec.location_ids.ids
                    ):
                        raise ValidationError(
                            _(
                                "Cannot have more than one in-progress inventory adjustment "
                                "affecting the same location or product at the same time."
                            )
                        )

    @api.constrains("product_selection", "product_ids")
    def _check_one_product_in_product_selection(self):
        for rec in self:
            if len(rec.product_ids) > 1:
                if rec.product_selection == "one":
                    raise ValidationError(
                        _(
                            "When 'Product Selection: One Product' is selected"
                            " you are only able to add one product."
                        )
                    )
                elif rec.product_selection == "lot":
                    raise ValidationError(
                        _(
                            "When 'Product Selection: Lot Serial Number' is selected"
                            " you are only able to add one product."
                        )
                    )

    def _get_inventory_product_domain(self):
        self.ensure_one()
        product_selection = self.product_selection
        domain = []
        if product_selection == "all":
            domain = self._get_inventory_product_domain_all()
        elif product_selection == "manual":
            domain = self._get_inventory_product_domain_manual()
        elif product_selection == "one":
            domain = self._get_inventory_product_domain_one()
        elif product_selection == "lot":
            domain = self._get_inventory_product_domain_lot()
        elif product_selection == "category":
            domain = self._get_inventory_product_domain_category()
        return expression.AND(
            [
                [
                    ("type", "=", "product"),
                ],
                domain,
            ]
        )

    def _get_inventory_product_domain_all(self):
        self.ensure_one()
        return [
            ("type", "=", "product"),
        ]

    def _get_inventory_product_domain_manual(self):
        self.ensure_one()
        return [
            ("id", "in", self.product_ids.ids),
        ]

    def _get_inventory_product_domain_one(self):
        self.ensure_one()
        return [
            ("id", "in", self.product_ids.ids),
        ]

    def _get_inventory_product_domain_lot(self):
        self.ensure_one()
        return [
            ("id", "in", self.product_ids.ids),
        ]

    def _get_inventory_product_domain_category(self):
        self.ensure_one()
        category = self.category_id
        return [
            "|",
            ("categ_id", "=", category.id),
            ("categ_id", "in", category.child_id.ids),
        ]

    def _get_quants_values(self):
        self.ensure_one()
        product_domain = self._get_inventory_product_domain()
        products = self.env["product.product"].search(product_domain)
        inv_lots = self.lot_ids
        quants_values = []
        locations = self._get_locations()
        for product in products:
            if product.tracking in ("lot", "serial"):
                product_lots = self._get_product_lots(product)
                for lot in product_lots:
                    if inv_lots and lot not in inv_lots:
                        continue
                    quants_values.extend(
                        self._get_new_quants_values(product, locations, lot_id=lot.id)
                    )
            else:
                quants_values.extend(self._get_new_quants_values(product, locations))
        return quants_values

    def _get_new_quant_base_values(self, product, **kwargs):
        self.ensure_one()
        values = {
            "product_id": product.id,
            "user_id": self.env.user.id,
            "stock_inventory_ids": [(4, self.id)],
        }
        values.update(kwargs)
        return values

    def _get_new_quants_values(self, product, locations, **kwargs):
        base_values = self._get_new_quant_base_values(product, **kwargs)
        quants_values = []
        for location in locations:
            values = base_values.copy()
            values["location_id"] = location.id
            quants_values.append(values)
        return quants_values

    def _get_locations(self):
        self.ensure_one()
        locations = self.location_ids
        if self.exclude_sublocation:
            domain = [("id", "in", locations.ids)]
        else:
            domain = [
                ("location_id", "child_of", locations.child_internal_location_ids.ids)
            ]
        return self.env["stock.location"].search(domain)

    def _get_product_lots(self, product):
        self.ensure_one()
        return self.env["stock.lot"].search(
            [
                ("product_id", "=", product.id),
            ]
        )
