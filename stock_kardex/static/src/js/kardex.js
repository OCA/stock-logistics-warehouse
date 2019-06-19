odoo.define('stock_kardex.kardex', function (require) {
"use strict";


var core = require('web.core');
var KanbanRecord = require('web.KanbanRecord');
var basicFields = require('web.basic_fields');
var field_registry = require('web.field_registry');
var DebouncedField = basicFields.DebouncedField;
var FieldInteger = basicFields.FieldInteger;

KanbanRecord.include({

    _openRecord: function () {
        if (this.modelName === 'stock.kardex'
            && this.$el.hasClass("open_kardex_screen")) {
            var self = this;
            this._rpc({
                method: 'action_open_screen',
                model: self.modelName,
                args: [self.id],
            }).then(function (result) {
                self.do_action(result);
            });
        } else {
            this._super.apply(this, arguments);
        }
    },

});

var ExitButton = FieldInteger.extend({
    tagName: 'button',
    className: 'btn btn-danger btn-block btn-lg o_kardex_exit',
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
        this.do_action('stock_kardex.stock_kardex_action', {
            clear_breadcrumbs: true,
        });
    },
});

var KardexTrayMatrixField = DebouncedField.extend({
    className: 'o_field_kardex_tray_matrix',
    tagName: 'canvas',
    supportedFieldTypes: ['serialized'],

    cellColorEmpty: '#ffffff',
    cellColorNotEmpty: '#4e6bfd',
    selectedColor: '#08f46b',
    selectedLineWidth: 5,
    globalAlpha: 0.8,
    cellPadding: 2,

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
            // _super calls _render(), but the function
            // resizeCanvasToDisplaySize would resize the canvas
            // to 0 because the actual canvas would still be unknown.
            // Call again _render() here but through a setTimeout to
            // let the js renderer thread catch up.
            self._ready = true;
            return self._resizeDebounce();
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
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;

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


field_registry.add('exit_button', ExitButton);
field_registry.add('kardex_tray_matrix', KardexTrayMatrixField);

return {
    ExitButton: ExitButton,
    KardexTrayMatrixField: KardexTrayMatrixField
};

});
