import {KanbanRecord} from "@web/views/kanban/kanban_record";
import {StockLotCatalogOrderLine} from "./order_line/order_line.esm";
import {rpc} from "@web/core/network/rpc";
import {useDebounced} from "@web/core/utils/timing";
import {useSubEnv} from "@odoo/owl";

export class StockLotCatalogKanbanRecord extends KanbanRecord {
    static template = "StockLotCatalogKanbanRecord";
    static components = {
        ...KanbanRecord.components,
        StockLotCatalogOrderLine,
    };

    setup() {
        super.setup();
        this.debouncedUpdateQuantity = useDebounced(this._updateQuantity, 500, {
            execBeforeUnmount: true,
        });

        useSubEnv({
            currencyId: this.props.record.context.lot_catalog_currency_id,
            orderId: this.props.record.context.lot_catalog_order_id,
            orderResModel: this.props.record.context.lot_catalog_order_model,
            digits: this.props.record.context.lot_catalog_digits,
            displayUoM: this.props.record.context.display_uom,
            precision: this.props.record.context.precision,
            lotId: this.props.record.resId,
            addLot: this.addLot.bind(this),
            removeLot: this.removeLot.bind(this),
            increaseQuantity: this.increaseQuantity.bind(this),
            setQuantity: this.setQuantity.bind(this),
            decreaseQuantity: this.decreaseQuantity.bind(this),
            childField: this.props.record.context?.child_field,
        });
    }

    get orderLineComponent() {
        return StockLotCatalogOrderLine;
    }

    get lotCatalogData() {
        return this.props.record.lotCatalogData;
    }

    onGlobalClick(ev) {
        // Avoid a concurrent update when clicking on the buttons (that are inside the record)
        if (ev.target.closest(".o_stock_lot_catalog_cancel_global_click")) {
            return;
        }
        if (this.lotCatalogData.quantity === 0) {
            this.addLot();
        } else {
            this.increaseQuantity();
        }
    }

    // --------------------------------------------------------------------------
    // Data Exchanges
    // --------------------------------------------------------------------------

    async _updateQuantity() {
        const price = await this._updateQuantityAndGetPrice();
        this.lotCatalogData.price = parseFloat(price);
    }

    _updateQuantityAndGetPrice() {
        return rpc(
            "/stock_lot/catalog/update_order_line_info",
            this._getUpdateQuantityAndGetPriceParams()
        );
    }

    _getUpdateQuantityAndGetPriceParams() {
        return {
            order_id: this.env.orderId,
            lot_id: this.env.lotId,
            quantity: this.lotCatalogData.quantity,
            res_model: this.env.orderResModel,
            child_field: this.env.childField,
        };
    }

    // --------------------------------------------------------------------------
    // Handlers
    // --------------------------------------------------------------------------

    updateQuantity(quantity) {
        if (this.lotCatalogData.readOnly) {
            return;
        }
        this.lotCatalogData.quantity = quantity || 0;
        this.debouncedUpdateQuantity();
    }

    /**
     * Add the lot to the order
     * @param {Qty} qty
     */
    addLot(qty = 1) {
        this.updateQuantity(qty);
    }

    /**
     * Remove the lot to the order
     */
    removeLot() {
        this.updateQuantity(0);
    }

    /**
     * Increase the quantity of the lot on the order line.
     * @param {Qty} qty
     */
    increaseQuantity(qty = 1) {
        this.updateQuantity(this.lotCatalogData.quantity + qty);
    }

    /**
     * Set the quantity of the lot on the order line.
     *
     * @param {Event} event
     */
    setQuantity(event) {
        this.updateQuantity(parseFloat(event.target.value));
    }

    /**
     * Decrease the quantity of the lot on the order line.
     */
    decreaseQuantity() {
        this.updateQuantity(parseFloat(this.lotCatalogData.quantity - 1));
    }
}
