Before using this module you should specify a putaway strategy on the stock location
you want to generate putaway for. You can find similar instructions on the 
stock_putaway_product module which is a dependency.

From a validated stock adjustment, use action -> Generate putaway per product.

Once this is done, the products of the stock adjustment without putaway locations 
will have one of the strategy defined on the inventory's location.
