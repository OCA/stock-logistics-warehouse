# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class RestrictedAccessMixin(models.AbstractModel):
    _name = "restricted.access.mixin"
    _description = "Restricted Access Mixin"

    has_restricted_access = fields.Boolean(
        compute="_compute_has_restricted_access",
        help="Indicates if this record has restricted access based on related fields",
    )

    def _compute_has_restricted_access(self):
        for record in self:
            record.has_restricted_access = False

    def _has_restricted_permission(self):
        return (
            self.env.user.has_group(
                "stock_product_security_restricted.group_product_creation_restricted"
            )
            or self.env.is_superuser()
        )

    def _check_restricted_field_changes(self, vals):
        """Check if restricted_access field is being changed without permission."""
        if not self._has_restricted_permission():
            # Only check models that have restricted_access field
            if "restricted_access" in self._fields and "restricted_access" in vals:
                # Check if any record would change restricted status
                changed = any(
                    record.restricted_access != vals["restricted_access"]
                    for record in self
                    if hasattr(record, "restricted_access")
                )
                if changed:
                    raise AccessError(
                        _(
                            "You do not have permission to change restricted access "
                            "settings for %(model)s. Only users with "
                            "'Product Creation - Restricted' group can modify the "
                            "restricted_access field.",
                            model=self._description.lower(),
                        )
                    )

    def _check_restricted_access_allowed(self):
        """Check that no records have has_restricted_access=True
        without proper permissions."""
        if not self._has_restricted_permission():
            # Use provided records or current recordset
            restricted = self.filtered("has_restricted_access")
            if restricted:
                raise AccessError(
                    _(
                        "You do not have permission to edit restricted "
                        "%(model)s: %(names)s",
                        model=self._description.lower(),
                        names=", ".join(restricted.mapped("display_name")),
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        result._check_restricted_access_allowed()
        return result

    def write(self, vals):
        self._check_restricted_access_allowed()
        result = super().write(vals)
        self._check_restricted_access_allowed()
        return result

    def unlink(self):
        self._check_restricted_access_allowed()
        return super().unlink()
