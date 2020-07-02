# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class VerticalLiftOperationPut(models.Model):
    _inherit = "vertical.lift.operation.put"

    # In the base module, when a good is scanned for a put-away, the user must
    # then scan a tray type, which will be used to find an available cell of
    # this type. When we use storage types (OCA/wms::stock_storage_type), we
    # shouldn't need to scan a tray type if we already have a storage type,
    # that could be used to find an available cell location for this type
    # (applying all the possible restrictions from storage type).

    def _transitions(self):
        transitions = super()._transitions()
        updated_transitions = []
        for transition in transitions:
            states = (transition.current_state, transition.next_state)
            if states == ("scan_tray_type", "save"):
                # insert new transitions just before the normal transition
                # scanning the tray type, that will bypass it when we have
                # a storage type
                updated_transitions.append(
                    self.Transition(
                        "scan_tray_type",
                        "save",
                        lambda self: self._has_storage_type()
                        and self._putaway_with_storage_type(),
                        # this is the trick that makes the transition applies
                        # its function and directly jumps to save
                        direct_eval=True,
                    )
                )
                updated_transitions.append(
                    self.Transition(
                        "scan_tray_type",
                        "scan_source",
                        # the transition above returned False because it could
                        # not find a free space, in that case, abort the
                        # put-away for this line in this shuttle
                        lambda self: self._has_storage_type()
                        and self._put_away_with_storage_type_failed()
                        and self.clear_current_move_line(),
                        # this is the trick that makes the transition applies
                        # its function and directly jumps to save
                        direct_eval=True,
                    )
                )
                # if none of the 2 transitions above is applied (because
                # self._has_storage_type() is False), the state remains
                # `scan_tray_type`, for the base transition doesn't have
                # `direct_eval=True`
            updated_transitions.append(transition)

        return tuple(updated_transitions)

    def _has_storage_type(self):
        move_line = self.current_move_line_id
        storage_type = move_line.package_id.package_storage_type_id
        return bool(storage_type)

    def _putaway_with_storage_type(self):
        move_line = self.current_move_line_id
        # Trigger the put-away application to place it somewhere inside
        # the current shuttle's location.
        new_destination = move_line.location_dest_id._get_pack_putaway_strategy(
            self.location_id, move_line.package_id.quant_ids, move_line.product_id
        )
        if new_destination and new_destination.vertical_lift_kind == "cell":
            move_line.location_dest_id = new_destination
            move_line.package_level_id.location_dest_id = new_destination
            self.fetch_tray()
            return True
        return False

    def _put_away_with_storage_type_failed(self):
        move_line = self.current_move_line_id
        storage_type = move_line.package_id.package_storage_type_id
        self.env.user.notify_warning(
            _("No free space found for storage type '{}' in shuttle '{}'").format(
                storage_type.name, self.name
            )
        )
        return True
