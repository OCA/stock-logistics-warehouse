/* Copyright 2020 Tecnativa - Ernesto Tejeda
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
 */

/*
This is a patch to add the o_list_button class to the qty_at_date_widget
widget column in the tree view. It is a way to trick Odoo into not taking
that column into account when determining which field to activate or
focus on when clicking on a cell while editing that view.
*/
odoo.define('web_group_by_percentage', function (require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        _renderBodyCell: function (record, node, colIndex, options) {
            var $td = this._super.apply(this, arguments);
            if (node.tag === 'widget' && node.attrs.name == "qty_at_date_widget") {
                $td.addClass("o_list_button");
            }
            return $td;
        }
    })
});
