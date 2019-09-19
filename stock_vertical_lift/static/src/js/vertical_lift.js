odoo.define('stock_vertical_lift.vertical_lift', function (require) {
"use strict";

var core = require('web.core');
var KanbanRecord = require('web.KanbanRecord');
var basicFields = require('web.basic_fields');
var field_registry = require('web.field_registry');
var FieldInteger = basicFields.FieldInteger;

KanbanRecord.include({

    _openRecord: function () {
        if (this.modelName === 'vertical.lift.shuttle'
            && this.$el.hasClass("open_shuttle_screen")) {
            var self = this;
            this._rpc({
                method: 'action_open_screen',
                model: self.modelName,
                args: [self.id],
            }).then(function (action) {
                self.trigger_up('do_action', {action: action});
            });
        } else {
            this._super.apply(this, arguments);
        }
    },

});

var ExitButton = FieldInteger.extend({
    tagName: 'button',
    className: 'btn btn-danger btn-block btn-lg o_shuttle_exit',
    events: {
        'click': '_onClick',
    },
    _render: function () {
        this.$el.text(this.string);
    },
    _onClick: function () {
        // the only reason to have this field widget is to be able
        // to inject clear_breadcrumbs in the action:
        // it will revert back to a normal - non-headless - view
        this.do_action('stock_vertical_lift.vertical_lift_shuttle_action', {
            clear_breadcrumbs: true,
        });
    },
});

field_registry.add('vlift_shuttle_exit_button', ExitButton);

return {
    ExitButton: ExitButton,
};

});
