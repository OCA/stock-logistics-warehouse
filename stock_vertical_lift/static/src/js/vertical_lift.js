odoo.define('stock_vertical_lift.vertical_lift', function (require) {
"use strict";

var core = require('web.core');
var KanbanRecord = require('web.KanbanRecord');
var basicFields = require('web.basic_fields');
var field_registry = require('web.field_registry');
var FormController = require('web.FormController');
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


FormController.include({
    init: function (parent, model, renderer, params) {
        this._super.apply(this, arguments);
        if(this.modelName.startsWith('vertical.lift.operation.')) {
            this.call('bus_service', 'addChannel', 'notify_vertical_lift_screen');
            this.call(
                'bus_service', 'on', 'notification',
                this, this.vlift_bus_notification
            );
            this.call('bus_service', 'startPolling');
        }
    },
    vlift_bus_notification: function (notifications) {
        var self = this;
        _.each(notifications, function (notification) {
            var channel = notification[0];
            var message = notification[1];
            if(channel === 'notify_vertical_lift_screen') {
                switch(message['action']) {
                case 'refresh':
                    self.vlift_bus_action_refresh(message['params']);
                    break;
                }
            }
        });
    },
    vlift_bus_action_refresh: function(params) {
        var selectedIds = this.getSelectedIds();
        if(!selectedIds.length){
            return;
        }
        var currentId = selectedIds[0];
        if(params['id'] === currentId && params['model'] == this.modelName){
            this.reload();
        }
    },
    destroy: function () {
        if(this.modelName.startsWith('vertical.lift.operation.')) {
            this.call('bus_service', 'deleteChannel', 'notify_vertical_lift_screen');
        }
        this._super.apply(this, arguments);
    }

});

field_registry.add('vlift_shuttle_exit_button', ExitButton);

return {
    ExitButton: ExitButton,
};

});
