# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockReserveArea(models.Model):
    _name = "stock.reserve.area"
    _description = "Stock Reserve Area"

    name = fields.Char()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )

    location_ids = fields.Many2many(
        "stock.location",
        relation="stock_reserve_area_stock_location_rel",
        column1="reserve_area_id",
        column2="location_id",
        help="Selected locations and their children will belong to the Reserve Area",
        domain="""[
        ('usage', 'in', ('internal', 'view')),
        ('company_id', '=', company_id)
        ]""",
    )
    child_area_ids = fields.Many2many(
        comodel_name="stock.reserve.area",
        relation="stock_reserve_area_rel",
        column1="stock_reserve_area_1",
        column2="stock_reserve_area_2",
        compute="_compute_child_area_ids",
        store=True,
    )
    parent_area_ids = fields.Many2many(
        comodel_name="stock.reserve.area",
        relation="stock_reserve_area_rel",
        column1="stock_reserve_area_2",
        column2="stock_reserve_area_1",
    )

    @api.depends("location_ids")
    def _compute_child_area_ids(self):
        computed_areas = self.env.context.get(
            "computed_areas", self.env["stock.reserve.area"]
        )
        for area in self:
            child_areas = self.env["stock.reserve.area"]
            if isinstance(area.id, models.NewId):
                continue
            location_areas = area.location_ids.mapped("reserve_area_ids") - area
            for location_area in location_areas:
                if all(
                    area.is_location_in_area(loc) for loc in location_area.location_ids
                ):
                    # All the locations in the location area are inside of our area.
                    # Therefore this is a child area.
                    child_areas |= location_area
            area.child_area_ids = child_areas
            computed_areas |= area
            if computed_areas:
                location_areas = location_areas - computed_areas
            location_areas.with_context(
                computed_areas=computed_areas
            )._compute_child_area_ids()

    @api.constrains("location_ids")
    def check_location_ids(self):
        # all areas have to be concentric areas.
        areas = self.location_ids.mapped(
            "reserve_area_ids"
        )  # areas that contain this area's locations
        for (
            area
        ) in areas:  # we loop through all areas to verify that they are concentric
            loc_areas = (
                area.location_ids.mapped("reserve_area_ids") - area
            )  # we check consistency for all areas of each location
            for loc_area in loc_areas:
                # or all loc_area locations are inside area or all area locations are
                # inside loc_area
                if not all(
                    area.is_location_in_area(loc) for loc in loc_area.location_ids
                ) and not all(
                    loc_area.is_location_in_area(loc) for loc in area.location_ids
                ):
                    raise UserError(_("All Areas must be concentric"))

    def is_location_in_area(self, location):
        return bool(location in self.location_ids)

    @api.onchange("location_ids")
    def _onchange_location_ids(self):
        # we add all child locations in the reserve area
        self.location_ids = self.env["stock.location"].search(
            [("id", "child_of", self.location_ids.ids)]
        )

    def _create_reservation_data_sql(self):
        self.env.cr.execute(
            """
            insert into stock_move_reserve_area_line
            (
            create_uid,
            create_date,
            move_id,
            product_id,
            reserve_area_id,
            reserved_availability,
            unreserved_qty
            )

            select
            1 as create_uid,
            current_timestamp as create_date,
            sm.id as move_id,
            sm.product_id as product_id,
            rel.stock_reserve_area_id as reserve_area_id,
            coalesce(sum(sml.reserved_uom_qty), 0) as reserved_availability,
            (sm.product_uom_qty - coalesce(sum(sml.reserved_uom_qty), 0)) as unreserved_qty
            from stock_move as sm
            inner join stock_move_stock_reserve_area_rel as rel on rel.stock_move_id = sm.id
            left join stock_move_line as sml on sml.move_id = sm.id
            where sm.state in ('assigned', 'partially_available')
            and sm.id not in (
            select move_id from stock_move_reserve_area_line group by move_id
            )
            and sm.location_dest_id not in (
                select location_id from stock_reserve_area_stock_location_rel
                where reserve_area_id = rel.stock_reserve_area_id
                )
            group by sm.id, rel.stock_reserve_area_id, sm.picking_id, sm.product_id
            having coalesce(sum(sml.reserved_uom_qty), 0) > 0
        """
        )

        self.env.cr.execute(
            """
            update stock_move as sm set area_reserved_availability = q.reserved_availability
            from (
            select move_id, min(reserved_availability) as reserved_availability
            from stock_move_reserve_area_line
            group by move_id
            ) as q
            where q.move_id = sm.id
        """
        )

    @api.model
    def action_initialize_reserve_area_data(self):
        ICP = self.env["ir.config_parameter"].sudo()
        self.env["stock.move"]._update_reserve_area_ids_sql()
        self._create_reservation_data_sql()
        ICP.set_param("stock_reserve_area.stock_reserve_area_init_mode", False)

    def update_reserve_area_lines(self, moves, locs_to_add, locs_to_delete):
        ICP = self.env["ir.config_parameter"].sudo()
        if ICP.get_param("stock_reserve_area.stock_reserve_area_init_mode"):
            # Do not update if the reserve data has not yet been initialized
            return
        for move in moves:
            reserve_area_line = self.env["stock.move.reserve.area.line"].search(
                [("move_id", "=", move.id), ("reserve_area_id", "=", self.id)]
            )
            if (
                move._is_out_area(self)
                and not reserve_area_line
                and (
                    move.location_id in locs_to_add
                    or move.location_dest_id in locs_to_delete
                )
            ):
                # The move is now an out move from the area because:
                # 1. The source location is now part of the area
                # 2. The destination location is no longer part of the area
                move.reserve_area_ids |= self
                if move._needs_area_reservation():
                    lines = move.create_reserve_area_lines()
                    lines._action_area_assign()
            elif not move._is_out_area(self) and (
                move.location_dest_id in locs_to_add
                or move.location_id in locs_to_delete
            ):
                # The move is no longer an out move because:
                # 1. The destination location is now part of the area.
                # 2. The source location is no longer part of the area.
                move.reserve_area_ids -= self
                if reserve_area_line:
                    reserve_area_line.unlink()
                    # TODO: Do this in the unlink
                    move._compute_area_reserved_availability()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for area in res:
            moves_impacted = self.env["stock.move"].search(
                [
                    ("location_id", "in", area.location_ids.ids),
                    ("location_dest_id", "not in", area.location_ids.ids),
                    (
                        "state",
                        "in",
                        ("confirmed", "assigned", "partially_available"),
                    ),
                ]
            )
            area.update_reserve_area_lines(moves_impacted, area.location_ids, [])
        return res

    def write(self, vals):
        location_ids = self.location_ids
        res = super().write(vals)
        if vals.get("location_ids"):
            to_write = self.env["stock.location"].browse(
                x for x in vals.get("location_ids")[0][2]
            )
            to_delete = location_ids - to_write
            to_add = to_write - location_ids
            moves_impacted = self.env["stock.move"].search(
                [
                    "|",
                    ("location_id", "in", to_add.ids + to_delete.ids),
                    ("location_dest_id", "in", to_add.ids + to_delete.ids),
                    (
                        "state",
                        "in",
                        ("confirmed", "partially_available", "assigned"),
                    ),
                ]
            )
            self.update_reserve_area_lines(moves_impacted, to_add, to_delete)
        return res

    def unlink(self):
        locations = self.location_ids
        res = super().unlink()
        moves_impacted = self.env["stock.move"].search(
            [
                ("location_id", "in", locations.ids),
                (
                    "state",
                    "in",
                    ("confirmed", "partially_available", "assigned"),
                ),
            ]
        )
        moves_impacted._compute_area_reserved_availability()
        return res

    def action_open_reserved_moves(self):
        self.ensure_one()
        move_reserve_area_lines = self.env["stock.move.reserve.area.line"].search(
            [("reserve_area_id", "=", self.id), ("reserved_availability", "!=", 0)]
        )
        view_id = self.env.ref(
            "stock_reserve_area.view_stock_move_reserve_area_line_tree"
        ).id
        context = dict(self.env.context or {})
        context["search_default_group_product_id"] = 1
        return {
            "name": _("Reserved in Areas lines"),
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "stock.move.reserve.area.line",
            "view_id": view_id,
            "target": "new",
            "search_view_id": self.env.ref(
                "stock_reserve_area.move_reserve_area_line_search"
            ).id,
            "domain": [("id", "in", move_reserve_area_lines.ids)],
            "context": context,
        }
