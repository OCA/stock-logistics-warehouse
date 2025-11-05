# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.image import is_image_size_above

from odoo.addons.web_editor.tools import get_video_embed_code, get_video_thumbnail


class StockLotImage(models.Model):
    _name = "stock.lot.image"
    _description = "Stock Lot Image"
    _inherit = ["image.mixin"]
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Lot",
        ondelete="cascade",
        index=True,
    )
    video_url = fields.Char(
        string="Video URL",
        help="URL of a video for showcasing your lot.",
    )
    embed_code = fields.Html(compute="_compute_embed_code", sanitize=False)
    can_image_1024_be_zoomed = fields.Boolean(
        string="Can Image 1024 be zoomed",
        compute="_compute_can_image_1024_be_zoomed",
        store=True,
    )

    @api.depends("image_1920", "image_1024")
    def _compute_can_image_1024_be_zoomed(self):
        for image in self:
            image.can_image_1024_be_zoomed = image.image_1920 and is_image_size_above(
                image.image_1920, image.image_1024
            )

    @api.depends("video_url")
    def _compute_embed_code(self):
        for image in self:
            image.embed_code = get_video_embed_code(image.video_url) or False

    @api.onchange("video_url")
    def _onchange_video_url(self):
        if not self.image_1920:
            thumbnail = get_video_thumbnail(self.video_url)
            self.image_1920 = thumbnail and base64.b64encode(thumbnail) or False

    @api.constrains("video_url")
    def _check_valid_video_url(self):
        for image in self:
            if image.video_url and not image.embed_code:
                raise ValidationError(
                    self.env._(
                        "Provided video URL for '%s' is not valid. Please enter a "
                        "valid video URL.",
                        image.name,
                    )
                )
