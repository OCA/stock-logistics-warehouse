* This new stock_inventory_revaluation_wip module will utilize the mrp_analytic_cost 'Cost Type' and 'Activity Driven Costs' components and bring them into the cost adjustment details. These additional components will need to be added to the cost adjustment details view so the user can see the impact of changing the activity driven cost products.

* The mrp_analytic_cost module adds a cost type which is then used on the work center. Work Center -> Cost Type

* The cost type contains 'Activity Driven Costs' which have 1 or more cost products, when added together calculate the 'Cost per hour' on the work center. (Just additional info: accounting entries use these products during the manufacturing process to show more detailed work in progress (WIP) during material consumption)
