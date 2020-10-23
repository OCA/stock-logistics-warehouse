# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

import itertools


class PullListWizard(models.TransientModel):
    _name = "stock.pull.list.wizard"
    _description = "Stock Pull List Wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        company = self.env.user.company_id
        wh = self.env["stock.warehouse"].search(
            [("company_id", "=", company.id)], limit=1)
        res.update({
            "warehouse_id": wh.id,
            "location_id": wh.lot_stock_id.id,
        })
        return res

    location_id = fields.Many2one(
        comodel_name="stock.location",
        required=True,
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
    )
    line_ids = fields.One2many(
        comodel_name="stock.pull.list.wizard.line",
        inverse_name="wizard_id",
        readonly=True,
    )
    # Step 1 - filtering options.
    exclude_reserved = fields.Boolean()
    location_dest_id = fields.Many2one(
        string="Destination Location",
        comodel_name="stock.location",
    )
    date_to = fields.Date()
    consolidate_by_product = fields.Boolean(
        help="All needs for each product will be grouped in one line, "
             "disregarding date.",
    )
    procurement_group_ids = fields.Many2many(
        comodel_name="procurement.group"
    )
    # Step 2 - filtering options.
    select_all = fields.Boolean(default=True)
    rule_action = fields.Selection(
        selection=lambda self: self.env["stock.rule"]._fields["action"].selection,
    )
    available_in_source_location = fields.Boolean(
        help="Select only rules with enough available stock in source "
             "location. Applies for rules with a source location.",
    )
    # Step 2 - grouping options.
    max_lines = fields.Integer()
    group_by_rule = fields.Boolean()

    def _get_moves_demand_domain(self):
        self.ensure_one()
        domain = [
            ("location_id", "child_of", self.location_id.id),
            ("state", "not in", ("draft", "done", "cancel")),
        ]
        if self.location_dest_id:
            domain.append(("location_dest_id", "=", self.location_dest_id.id))
        if self.exclude_reserved:
            domain.append(("state", "not in", ("assigned",)))
        if self.date_to:
            domain.append(("date_expected", "<=", self.date_to))
        if self.procurement_group_ids:
            domain.append(("group_id", "in", self.procurement_group_ids.ids))
        return domain

    def _get_moves_incoming_domain(self):
        self.ensure_one()
        domain = [
            ("location_dest_id", "child_of", self.location_id.id),
            ("state", "not in", ("draft", "done", "cancel")),
        ]
        if self.date_to:
            domain.append(("date_expected", "<=", self.date_to))
        return domain

    @api.model
    def _prepare_line_values(self, key, demand_qty, supply_qty):
        product, location, date_expected = key
        rule = self._get_stock_rule_id(product, location)
        global qty_assigned
        prev = qty_assigned.setdefault(product, 0.0)
        qty_available = self._get_available_qty(product, location) - prev
        need_without_stock = max(demand_qty - supply_qty, 0.0)
        qty_assigned_now = min(qty_available, need_without_stock)
        qty_needed = max(demand_qty - qty_available - supply_qty, 0.0)
        qty_assigned[product] = prev + qty_assigned_now
        return {
            "product_id": product,
            "location_id": location,
            "date_expected": date_expected,
            "stock_rule_id": rule.id if rule else False,
            "raw_demand_qty": demand_qty,
            "available_qty": qty_available,
            "incoming_qty": supply_qty,
            "needed_qty": qty_needed,
        }

    def _get_available_qty(self, product, location):
        product_obj = self.env["product.product"]
        product_l = product_obj.with_context(
            {"location": location.id}).browse(product.id)
        if self.exclude_reserved:
            return product_l.qty_available_not_res
        return product_l.qty_available

    @api.model
    def _get_stock_rule_id(self, product_id, location_id):
        values = {
            "warehouse_id": self.warehouse_id,
            "company_id": self.env.user.company_id,
        }
        stock_rule_id = self.env["procurement.group"]._get_rule(
            product_id, location_id, values)
        return stock_rule_id

    def action_prepare(self):
        domain = self._get_moves_demand_domain()
        # `read_group` is not possible here because of the date format the
        # method returns.
        demand_moves = self.env["stock.move"].search(
            domain, order="date_expected asc")
        demand_dict = {}
        force_date = fields.Date.today() if self.consolidate_by_product \
            else False
        for demand in demand_moves:
            key = (
                demand.product_id, demand.location_id,
                fields.Date.to_date(demand.date_expected)
                if not force_date else force_date,
            )
            prev = demand_dict.setdefault(key, 0.0)
            # TODO: when exclude_reserved is selected, handle partially avail.
            demand_dict[key] = prev + demand.product_uom_qty

        domain = self._get_moves_incoming_domain()
        incoming_moves = self.env["stock.move"].search(
            domain, order="date_expected asc")
        incoming_dict = {}
        for supply in incoming_moves:
            move_for_date = demand_moves.filtered(
                lambda m: m.product_id == supply.product_id and
                m.date_expected >= supply.date_expected)
            if move_for_date:
                date_selected = move_for_date[0].date_expected \
                    if not force_date else force_date
            else:
                # Supply is later than last demand -> ignore it.
                continue
            key = (
                supply.product_id, supply.location_dest_id,
                fields.Date.to_date(date_selected),
            )
            prev = incoming_dict.setdefault(key, 0.0)
            incoming_dict[key] = prev + supply.product_uom_qty

        lines = []
        global qty_assigned
        qty_assigned = {}
        for key, demand_qty in demand_dict.items():
            supply_qty = incoming_dict.get(key, 0.0)
            lines.append((0, 0, self._prepare_line_values(
                key, demand_qty, supply_qty)))
        self.update({
            "line_ids": lines,
        })
        res = self._act_window_pull_list_step_2()
        return res

    def _act_window_pull_list_step_2(self):
        view_id = self.env.ref(
            "stock_pull_list.view_run_stock_pull_list_wizard_wizard_step_2").id
        res = {
            "name": _("Pull List"),
            "src_model": "stock.pull.list.wizard",
            "view_type": "form",
            "view_mode": "form",
            "view_id": view_id,
            "target": "new",
            "res_model": "stock.pull.list.wizard",
            "res_id": self.id,
            "type": "ir.actions.act_window",
        }
        return res

    def action_update_selected(self):
        for line in self.line_ids:
            if self.select_all:
                line.selected = True
                continue
            rule_invalid = self.rule_action and \
                self.rule_action != line.stock_rule_id.action
            if self.available_in_source_location:
                available = line._is_available_in_source_location()
            else:
                available = True
            if rule_invalid or not available:
                line.selected = False
            else:
                line.selected = True
        # The wizard must be reloaded in order to show the new product lines
        res = self._act_window_pull_list_step_2()
        return res

    def _prepare_procurement_values(self, date, group):
        values = {
            "date_planned": date,
            "warehouse_id": self.warehouse_id,
            "company_id": self.env.user.company_id,
            "group_id": group,
        }
        return values

    def _get_fields_for_keys(self):
        fields = []
        if self.group_by_rule:
            fields.append("stock_rule_id")
        return fields

    def _get_procurement_group_keys(self):
        fields = self._get_fields_for_keys()
        if not fields:
            return [False]
        options_list = []
        for f in fields:
            # Many2many only field type supported. As more needs arise, this
            # can be extended
            options_list.append(self.line_ids.mapped(f).ids)
        return list(itertools.product(*options_list))

    def _prepare_proc_group_values(self):
        # TODO: use special secuence to name procurement groups of pull lists.
        return {}

    def action_procure(self):
        self.ensure_one()
        lines_obj = self.env["stock.pull.list.wizard.line"]
        errors = []
        proc_groups = []
        # User requesting the procurement is passed by context to be able to
        # update final MO, PO or trasfer with that information.
        # TODO: migration to v13: requested_uid is not needed.
        pg_obj = self.env["procurement.group"].with_context(
            requested_uid=self.env.user)
        grouping_keys = self._get_procurement_group_keys()
        fields = self._get_fields_for_keys()
        for gk in grouping_keys:
            domain = [("wizard_id", "=", self.id), ("needed_qty", ">", 0.0)]
            for i, f in enumerate(fields):
                domain.append((f, "=", gk[i]))
            n = 0
            lines = lines_obj.search(domain)
            if not lines:
                continue
            group = pg_obj.create(self._prepare_proc_group_values())
            proc_groups.append(group.id)
            for line in lines.filtered(lambda l: l.selected):
                n += 1
                if 0 < self.max_lines < n:
                    n = 0
                    group = pg_obj.create(self._prepare_proc_group_values())
                    proc_groups.append(group.id)

                values = self._prepare_procurement_values(
                    line.date_expected, group)
                try:
                    pg_obj.run(
                        line.product_id,
                        line.needed_qty,
                        line.product_id.uom_id,
                        line.location_id,
                        "Pull List %s" % self.id,
                        "Pull List %s" % self.id,
                        values
                    )
                except UserError as error:
                    errors.append(error.name)
                if errors:
                    raise UserError("\n".join(errors))
        res = {
            "name": _("Generated Procurement Groups"),
            "src_model": "stock.pull.list.wizard",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "procurement.group",
            "type": "ir.actions.act_window",
            "domain": str([("id", "in", proc_groups)]),
        }
        return res


class PullListWizardLine(models.TransientModel):
    _name = "stock.pull.list.wizard.line"
    _description = "Stock Pull List Wizard Line"

    wizard_id = fields.Many2one(
        comodel_name="stock.pull.list.wizard",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
    )
    date_expected = fields.Date()
    available_qty = fields.Float()
    incoming_qty = fields.Float()
    raw_demand_qty = fields.Float()
    needed_qty = fields.Float()
    stock_rule_id = fields.Many2one(
        comodel_name="stock.rule",
    )
    selected = fields.Boolean(default=True)

    def _is_available_in_source_location(self):
        if not self.stock_rule_id.location_src_id:
            return False
        qty_avail = self.wizard_id._get_available_qty(
            self.product_id, self.stock_rule_id.location_src_id)
        return qty_avail > self.needed_qty
