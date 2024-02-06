By activating the "Create Rules Automatically" on a reordering rule template,
you are able to select a list of products. Any change on the template will then
be replicated on the products Reordering Rules. The change is not immediate as
it is processed by a scheduled action.

Aditionally, minimum and maximum quantity fields can be computed automatically
if desired for the set of products and according to the desired criteria for
the time range given. To do so:

#. In an Orderpoint template, check "Auto minimum" or "Auto maximum" or both.
#. The criteria fields for either one or another are visible now.
#. Select a time range of moves to evalute. For every product a history of
   the resulting stock for every move in such range and the location given
   on the Orderpoint template will be obtained.
#. Select a criteria method to compute the minimum o maximum quantity:

   - Maximum: the maximum stock value for the given period.
   - Most frequent: the median of the history of stock values for the specified
     range. Useful when a large amount of history values are obtained, as it
     tends to avoid deviation caused by extreme values in a common avarage.
   - Average: Arithmetic mean of the stock history.
   - Minimum: the minimum stock value for the given period.

Lastly, you can promptly create Reordering Rules for a product or a product
template using the "Reordering Rules Generator". Note that it will replace all
the existing rules for the product. You will usually not want to use this
feature on products that have Automatic Reordering Rules Templates.
