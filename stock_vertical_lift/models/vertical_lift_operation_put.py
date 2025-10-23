# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.osv.expression import AND


class VerticalLiftOperationPut(models.Model):
    _name = "vertical.lift.operation.put"
    _inherit = "vertical.lift.operation.transfer"
    _description = "Vertical Lift Operation Put"

    _initial_state = "scan_source"

    def _selection_states(self):
        return [
            ("scan_source", "Scan a package, product or lot to put-away"),
            ("scan_tray_type", "Scan Tray Type"),
            ("save", "Put goods in tray and save"),
            ("release", "Release"),
        ]

    def _transitions(self):
        return (
            self.Transition(
                "scan_source",
                "scan_tray_type",
                # transition only if a move line has been selected
                # (by on_barcode_scanner)
                lambda self: self.current_move_line_id,
            ),
            self.Transition("scan_tray_type", "save"),
            self.Transition("save", "release", lambda self: self.process_current()),
            self.Transition(
                "release", "scan_source", lambda self: self.clear_current_move_line()
            ),
        )

    def _domain_move_lines_to_do(self):
        domain = [
            ("state", "in", ("assigned", "partially_available")),
            ("location_dest_id", "child_of", self.location_id.id),
        ]
        return domain

    def _domain_move_lines_to_do_all(self):
        shuttle_locations = self.env["stock.location"].search(
            [("vertical_lift_kind", "=", "view")]
        )
        domain = [
            ("state", "in", ("assigned", "partially_available")),
            ("location_dest_id", "child_of", shuttle_locations.ids),
        ]
        return domain

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        if self.step() == "scan_source":
            self._scan_source_action(barcode)
        elif self.step() in ("scan_tray_type", "save"):
            # note: we must be able to scan a different tray type when we are
            # in the save step too, in case we couldn't put it in the first one
            # for some reason.
            self._scan_tray_type_action(barcode)

    def _scan_source_action(self, barcode):
        line = self._find_move_line(barcode)
        if line:
            self.current_move_line_id = line
            self.next_step()
        else:
            self.env.user.notify_warning(
                self.env._(
                    "No move line found for barcode %(barcode)s", barcode=barcode
                ),
                params=self._get_user_notification_params(),
            )

    def _scan_tray_type_action(self, barcode):
        tray_type = self._find_tray_type(barcode)
        if tray_type:
            if self._assign_available_cell(tray_type):
                self.fetch_tray()
                if self.step() == "scan_tray_type":
                    # when we are in "save" step, stay here
                    self.next_step()
            else:
                self.env.user.notify_warning(
                    self.env._(
                        "No free space for tray type %(name)s in this shuttle.",
                        name=tray_type.display_name,
                    ),
                    params=self._get_user_notification_params(),
                )
        else:
            self.env.user.notify_warning(
                self.env._(
                    "No tray type found for barcode %(barcode)s", barcode=barcode
                ),
                params=self._get_user_notification_params(),
            )

    def _find_tray_type(self, barcode):
        return self.env["stock.location.tray.type"].search(
            [("code", "=", barcode)], limit=1
        )

    def _find_move_line(self, barcode):
        package = self.env["stock.quant.package"].search([("name", "=", barcode)])
        if package:
            return self._find_move_line_for_package(package)

        lot = self.env["stock.lot"].search([("name", "=", barcode)])
        if lot:
            return self._find_move_line_for_lot(package)

        product = self.env["product.product"].search([("barcode", "=", barcode)])
        if not product:
            packaging = self.env["product.packaging"].search(
                [("product_id", "!=", False), ("barcode", "=", barcode)]
            )
            product = packaging.product_id
        if product:
            return self._find_move_line_for_product(product)

    def _check_move_lines_to_merge(self, lines):
        check_fields = ["product_id", "lot_id", "product_uom_id"]
        for field in check_fields:
            values = lines.mapped(field)
            if len(values) > 1:
                return False
            if len(values) == 1 and lines.filtered(
                lambda line, field=field: not line[field]
            ):
                return False
        return True

    def _find_move_line_for_package(self, package):
        domain = AND(
            [self._domain_move_lines_to_do_all(), [("package_id", "in", package.ids)]]
        )
        lines = self.env["stock.move.line"].search(domain)
        if len(lines) > 1:
            # Multiple move lines in the same package,
            # they need to be merged if possible
            # Or Odoo will raise an exception
            # because the move is done one line at at time
            picking = fields.first(lines.picking_id)
            if picking._check_move_lines_map_quant_package(package):
                # Fist merge all lines in the same move
                move = lines.move_id._merge_moves()
                if len(move) == 1 and len(move.move_line_ids) > 1:
                    # Now we have one move, let's merge the move lines together
                    lines = move.move_line_ids
                    line_keep = fields.first(lines)
                    if self._check_move_lines_to_merge(lines):
                        values = {
                            "quantity": sum(lines.mapped("quantity")),
                        }
                        line_keep.write(values)
                        other_lines = lines - line_keep
                        other_lines.unlink()
                    lines = line_keep
        return fields.first(lines)

    def _find_move_line_for_lot(self, lot):
        domain = AND(
            [
                self._domain_move_lines_to_do_all(),
                [
                    ("lot_id", "=", lot.id),
                    # if the lot is in a package, the package must be scanned
                    ("package_id", "=", False),
                ],
            ]
        )
        return self.env["stock.move.line"].search(domain, limit=1)

    def _find_move_line_for_product(self, product):
        domain = AND(
            [
                self._domain_move_lines_to_do_all(),
                [
                    ("product_id", "=", product.id),
                    # if the lot is in a package, the package must be scanned
                    ("package_id", "=", False),
                ],
            ]
        )
        return self.env["stock.move.line"].search(domain, limit=1)

    def _check_tray_type(self, barcode):
        location = self.current_move_line_id.location_dest_id
        tray_type = location.cell_in_tray_type_id
        return barcode == tray_type.code

    def _assign_available_cell(self, tray_type):
        locations = self.env["stock.location"].search(
            [
                ("id", "child_of", self.location_id.id),
                ("cell_in_tray_type_id", "=", tray_type.id),
            ]
        )
        location = fields.first(
            locations.filtered(lambda loc: not loc.tray_cell_contains_stock)
        )
        if location:
            self.current_move_line_id.location_dest_id = location
            self.current_move_line_id.package_level_id.location_dest_id = location
            return True
        return False

    def fetch_tray(self):
        self.current_move_line_id.fetch_vertical_lift_tray_dest()

    def button_release(self):
        res = super().button_release()
        if self.count_move_lines_to_do_all() == 0:
            # we don't need to release (close) the tray until we have reached
            # the last line: the release is implicit when a next line is
            # fetched if the tray change
            self.shuttle_id.release_vertical_lift_tray()
            # sorry not sorry
            res = self._rainbow_man()
        return res
