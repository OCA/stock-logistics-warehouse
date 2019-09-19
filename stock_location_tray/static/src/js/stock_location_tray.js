odoo.define('stock_location_tray.tray', function (require) {
"use strict";

var core = require('web.core');
var KanbanRecord = require('web.KanbanRecord');
var basicFields = require('web.basic_fields');
var field_registry = require('web.field_registry');
var DebouncedField = basicFields.DebouncedField;

/**
* Shows a canvas with the Tray's cells
*
* An action can be configured which is called when a cell is clicked.
* The action must be an action.multi, it will receive the x and y positions
* of the cell clicked (starting from 0). The action must be configured in
* the options of the field and be on the same model:
*
* <field name="tray_matrix"
*        widget="location_tray_matrix"
*        options="{'click_action': 'action_tray_matrix_click'}"
*        />
*
*/
var LocationTrayMatrixField = DebouncedField.extend({
    className: 'o_field_location_tray_matrix',
    tagName: 'canvas',
    supportedFieldTypes: ['serialized'],
    events: {
        'click': '_onClick',
    },

    cellColorEmpty: '#ffffff',
    cellColorNotEmpty: '#4e6bfd',
    selectedColor: '#08f46b',
    selectedLineWidth: 5,
    globalAlpha: 0.8,
    cellPadding: 2,

    init: function (parent, name, record, options) {
        this._super.apply(this, arguments);
        this.nodeOptions = _.defaults(this.nodeOptions, {});
        this.clickAction = 'clickAction' in (options || {}) ? options.clickAction : this.nodeOptions.click_action;
    },

    isSet: function () {
        if (Object.keys(this.value).length === 0) {
            return false;
        }
        if (this.value.cells.length === 0) {
            return false;
        }
        return this._super.apply(this, arguments);
    },

    start: function () {
        // Setup resize events to redraw the canvas
        this._resizeDebounce = this._resizeDebounce.bind(this);
        this._resizePromise = null;
        $(window).on('resize', this._resizeDebounce);

        var self = this;
        return this._super.apply(this, arguments).then(function () {
            if (self.clickAction) {
                self.$el.css('cursor', 'pointer');
            }
            // _super calls _render(), but the function
            // resizeCanvasToDisplaySize would resize the canvas
            // to 0 because the actual canvas would still be unknown.
            // Call again _render() here but through a setTimeout to
            // let the js renderer thread catch up.
            self._ready = true;
            return self._resizeDebounce();
        });
    },

    _onClick: function (ev) {
        if (!this.isSet()) {
            return;
        }
        if (!this.clickAction) {
            return;
        }
        var width = this.canvas.width,
            height = this.canvas.height,
            rect = this.canvas.getBoundingClientRect();

        var clickX = ev.clientX - rect.left,
            clickY = ev.clientY - rect.top;

        var cells = this.value.cells,
            cols = cells[0].length,
            rows = cells.length;

        // we remove 1 to start counting from 0
        var coordX = Math.ceil(clickX * cols / width) - 1,
            coordY = Math.ceil(clickY * rows / height) - 1;
        // if we click on the last pixel on the bottom or the right
        // we would get an offset index
        if (coordX >= cols) { coordX = cols - 1; }
        if (coordY >= rows) { coordY = rows - 1; }

        // the coordinate we get when we click is from top,
        // but we are looking for the coordinate from the bottom
        // to match the user's expectations, invert Y
        coordY = Math.abs(coordY - rows + 1);

        var self = this;
        this._rpc({
            model: this.model,
            method: this.clickAction,
            args: [[this.res_id], coordX, coordY]
        })
        .then(function (action) {
            self.trigger_up('do_action', {action: action});
        });
    },

    /**
     * Debounce the rendering on resize.
     * It is useless to render on each resize event.
     *
     */
    _resizeDebounce: function(){
        clearTimeout(this._resizePromise);
        var self = this;
        this._resizePromise = setTimeout(function(){
            self._render();
        }, 20);
    },

    destroy: function () {
        $(window).off('resize', this._resizeDebounce);
        this._super.apply(this, arguments);
    },

    /**
     * Render the widget only when it is in the DOM.
     * We need the width and height of the widget to draw the canvas.
     *
     */
    _render: function () {
        if (this._ready) {
            return this._renderInDOM();
        }
        return $.when();
    },

    /**
     * Resize the canvas width and height to the actual size.
     * If we don't do that, it will automatically scale to the
     * CSS size with blurry squares.
     *
     */
    resizeCanvasToDisplaySize: function(canvas) {
        // look up the size the canvas is being displayed
        var width = canvas.clientWidth;
        var height = canvas.clientHeight;

        // If it's resolution does not match change it
        if (canvas.width !== width || canvas.height !== height) {
            canvas.width = width;
            canvas.height = height;
            return true;
        }

        return false;
    },

    /**
     * Resize the canvas, clear it and redraw the cells
     * Should be called only if the canvas is already in DOM
     *
     */
    _renderInDOM: function () {
        this.canvas = this.$el.find('canvas').context;
        var canvas = this.canvas;
        var ctx = canvas.getContext('2d');
        this.resizeCanvasToDisplaySize(ctx.canvas);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        if (this.isSet()) {
            var selected = this.value.selected || [];
            var cells = this.value.cells;
            this._drawMatrix(canvas, ctx, cells, selected);
        }
    },

    /**
     * Draw the cells in the canvas.
     *
     */
    _drawMatrix: function (canvas, ctx, cells, selected) {
        var colors = {
          0: this.cellColorEmpty,
          1: this.cellColorNotEmpty,
        };

        var cols = cells[0].length;
        var rows = cells.length;
        var selectedX, selectedY;
        if (selected.length) {
            selectedX = selected[0];
            // we draw top to bottom, but the highlighted cell should
            // be a coordinate from bottom to top: reverse the y axis
            selectedY = Math.abs(selected[1] - rows + 1);
        }

        var padding = this.cellPadding;
        var w = ((canvas.width - padding * cols) / cols);
        var h = ((canvas.height - padding * rows) / rows);

        ctx.globalAlpha = this.globalAlpha;
        // again, our matrix is top to bottom (0 is the first line)
        // but visually, we want them bottom to top
        var reversed_cells = cells.slice().reverse();
        for (var y = 0; y < rows; y++) {
            for (var x = 0; x < cols; x++) {
                ctx.fillStyle = colors[reversed_cells[y][x]];
                var fillWidth = w;
                var fillHeight = h;
                // cheat: remove the padding at bottom and right
                // the cells will be a bit larger but not really noticeable
                if (x === cols - 1) {fillWidth += padding;}
                if (y === rows - 1) {fillHeight += padding;}
                ctx.fillRect(
                    x * (w + padding), y * (h + padding),
                    fillWidth, fillHeight
                );
                if (selected && selectedX === x && selectedY === y) {
                    ctx.globalAlpha = 1.0;
                    ctx.strokeStyle = this.selectedColor;
                    ctx.lineWidth = this.selectedLineWidth;
                    ctx.strokeRect(x * (w + padding), y * (h + padding), w, h);
                    ctx.globalAlpha = this.globalAlpha;
                }
            }
        }
        ctx.restore();
    }
});


field_registry.add('location_tray_matrix', LocationTrayMatrixField);

return {
    LocationTrayMatrixField: LocationTrayMatrixField
};

});
