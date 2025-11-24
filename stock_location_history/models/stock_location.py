import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class StockLocation(models.Model):
    _inherit = "stock.location"

    track_stage = fields.Boolean(
        string="Track location stage?",
        default=False,
        help="If enabled, the location stages will be tracked.",
    )

    @api.onchange("track_stage")
    def _onchange_track_stage(self):
        if self.track_stage and not self.stage_id:
            # Assign default stage when enabling tracking
            default_stage = self.env["stock.location.stage"].search(
                [("is_default", "=", True)], limit=1
            )
            if default_stage:
                self.stage_id = default_stage
        elif not self.track_stage and self.stage_id:
            # Prevent disabling tracking if not on default stage
            default_stage = self.env["stock.location.stage"].search(
                [("is_default", "=", True)], limit=1
            )
            if default_stage and self.stage_id != default_stage:
                raise ValidationError(
                    _("Cannot disable stage tracking while not on the default stage.")
                )

    stage_id = fields.Many2one("stock.location.stage", string="Stage")
    lot_id = fields.Many2one("stock.lot")
    # product_id = fields.Many2one(related="lot_id.product_id", store=True)
    actual_product_id = fields.Many2one(
        "product.product", string="Product", domain=[("tracking", "=", "lot")]
    )
    last_stage_id = fields.Many2one("stock.location.stage", string="Last stage")
    last_stage_validated = fields.Boolean(
        string="Is the last stage progress validated?"
    )

    def open_location_history(self):
        self.ensure_one()
        return {
            "name": _("Location History"),
            "type": "ir.actions.act_window",
            "res_model": "stock.location.history",
            "view_mode": "list,form",
            "domain": [("location_id", "=", self.id)],
            "context": {"default_location_id": self.id},
        }

    @api.constrains("stage_id")
    def check_stage_change(self):
        default_stage = self.env["stock.location.stage"].search(
                [("is_default", "=", True)], limit=1
            )
        self.ensure_one()
        # Check if we're trying to disable track_stage when not on default stage
        # This runs when stage_id changes, so we check if track_stage is False
        # but stage_id is not empty
        if not self.track_stage and self.stage_id:
            if default_stage and self.stage_id != default_stage:
                raise ValidationError(
                    _("Cannot disable stage tracking while not on the default stage.")
                )
            
        if (not self.last_stage_id and not self.stage_id.is_default):
            if not self.actual_product_id:
                raise ValidationError(
                    _("A product must be assigned before changing stages.")
                )
            else:
                new_lot = self.macrolotCreation()
                self.lot_id = new_lot

        # Check if we're leaving the default stage; actual_product_id must be set
        if self.last_stage_id and self.last_stage_id.is_default and self.stage_id:
            # Check if we're moving away from default stage
            if (
                default_stage
                and self.last_stage_id == default_stage
                and self.stage_id != default_stage
            ):
                # If there's no product assigned, prevent the change
                if not self.actual_product_id:
                    raise ValidationError(
                        _("A product must be assigned before changing stages.")
                    )
                # If there is a product assigned, create a lot and assign it
                else:
                    new_lot = self.macrolotCreation()
                    self.lot_id = new_lot

        # Check if we're transitioning FROM a closed stage TO a default stage
        if (
            self.last_stage_id
            and self.last_stage_id.is_closed
            and self.stage_id
            and self.stage_id.is_default
        ):
            # Clean up lot_id and actual_product_id fields
            self.lot_id = False
            self.actual_product_id = False

        if self.stage_id and not any(
            g in self.env.user.groups_id for g in self.stage_id.change_group_ids
        ):
            raise ValidationError(_("You are not allowed to change the stage."))
        if (
            self.last_stage_id
            and self.last_stage_id.validation
            and not self.last_stage_validated
        ):
            raise ValidationError(_("Validation required"))
        if self.stage_id != self.last_stage_id and self.last_stage_id:
            if not self.validate_stage_route():
                raise ValidationError(_("Invalid stage change"))
            else:
                self.create_location_history(self.stage_id.name)
        self.last_stage_id = self.stage_id
        self.last_stage_validated = not self.stage_id.validation

    @api.constrains("location_history_ids")
    def check_last_history_change(self):
        last_history = self.env["stock.location.history"].search(
            [("location_id", "=", self.id)], order="create_date desc", limit=1
        )
        if not last_history:
            self.last_stage_validated = True
        else:
            if last_history.registry_type == "val":
                self.last_stage_validated = True

    def validate_stage_route(self):
        if not self.stage_id:
            return True
        destination_ids = self.last_stage_id.next_ids
        return self.stage_id in destination_ids

    def create_location_history(self, registry_type):
        history_vals = {
            "location_id": self.id,
            "lot_id": self.lot_id.id,
            "previous_stage_id": self.last_stage_id.id,
            "new_stage_id": self.stage_id.id,
            "registry_type": registry_type,
            "user_id": self.env.uid,
        }
        self.env["stock.location.history"].sudo().create(history_vals)

    def validate_stage(self):
        if not any(
            g in self.env.user.groups_id for g in self.stage_id.validation_group_ids
        ):
            raise ValidationError(_("You are not allowed to change the stage."))
        else:
            self.create_location_history("Validation")
            self.last_stage_validated = True

    def verifyBDSource(self):
        """Fetch batch data from external PLC and create related records."""
        warehouse_model = self.env["stock.warehouse"]
        try:
            warehouses = warehouse_model.search([("dbsource_id", "!=", False)])
        except ValueError:
            # Field dbsource_id doesn't exist (gaqsa_mrp not installed or not loaded)
            _logger.warning(
                "dbsource_id field not available in stock.warehouse. "
                "Please ensure gaqsa_mrp module is installed."
            )
            return
        except Exception as e:
            _logger.warning("Error searching warehouses with dbsource_id: %s", e)
            return
        if not warehouses:
            _logger.info("No warehouses with dbsource_id configured.")
            return
        for warehouse in warehouses:
            PLC_DB = warehouse.dbsource_id or False
        return PLC_DB

    def PLC_Complete(self):
        if self.getMacroFromPLC():
            self.updateMacroToPLC()
        else:
            self.pushMacroToPLC()

    def updateMacroToPLC(self):
        PLC_DB = self.verifyBDSource()

        try:
            with PLC_DB.connection_open() as conn:
                silo = self.name
                codmat = self.actual_product_id.default_code
                macrolote = self.lot_id.name

                query = """UPDATE Macrolotes SET Macrolote =?
                            WHERE CodMat=? AND Silo=?"""

                conn.execute(query, (macrolote, codmat, silo))
                conn.commit()

        except Exception as e:
            raise ValidationError(_(f"Error updating in MSSQL: {e}")) from e

    def pushMacroToPLC(self):
        PLC_DB = self.verifyBDSource()

        try:
            with PLC_DB.connection_open() as conn:
                silo = self.name
                codmat = self.actual_product_id.default_code
                nommat = self.actual_product_id.name
                macrolote = self.lot_id.name

                query = """INSERT INTO Macrolotes (Silo, CodMat, NomMat, Macrolote)
                                VALUES(?,?,?,?);"""
                conn.execute(query, (silo, codmat, nommat, macrolote))
                conn.commit()

        except Exception as e:
            raise ValidationError(_(f"Error inserting in MSSQL: {e}")) from e

    def getMacroFromPLC(self):
        PLC_DB = self.verifyBDSource()
        codmat = self.actual_product_id.default_code
        silo = self.name
        try:
            with PLC_DB.connection_open() as conn:
                query = (
                    "SELECT id, Silo, CodMat, NomMat, Macrolote "
                    "FROM Macrolotes WHERE CodMat=? AND Silo=?;"
                )

                result = conn.execute(query, (codmat, silo))

                rows = result.fetchall()

                if not rows:
                    return False
                else:
                    return True
        except Exception as e:
            raise ValidationError(_(f"Error querying in MSSQL: {e}")) from e
    def macrolotCreation(self):
        # Create a new lot with the requested naming convention
        # Format: <location_name>-<5-digit_consecutive_number>
        location_name = self.name.replace(" ", "_").upper()[
            :10
        ]  # Take first 10 chars, uppercase, remove spaces
        # Count existing lots for this location
        existing_lots = self.env["stock.lot"].search(
            [("name", "like", f"{location_name}-")]
        )
        next_number = len(existing_lots) + 1
        lot_name = f"{location_name}-{next_number:05d}"
        lot_vals = {
            "name": lot_name,
            "product_id": self.actual_product_id.id,
            "company_id": self.env.company.id,
            "location_id": self.id,
        }
        new_lot = self.env["stock.lot"].sudo().create(lot_vals)
        self.with_delay().PLC_Complete()
        return new_lot