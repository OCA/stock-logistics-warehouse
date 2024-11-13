When a picking is generated from a procurement evaluation
(e.g., from an orderpoint or MTO), the warehouse calendar
is used to calculate the expected dates for the picking and
its associated stock moves.

For instance, if a stock transfer from another warehouse requires
1 day to complete and the product is needed on a Monday,
the system will determine that the transfer must begin on the previous Friday.
This ensures the product arrives on time, considering the warehouse
operates under a Monday-to-Friday working calendar.
Without the calendar adjustment, the system might
incorrectly plan the transfer to start on Sunday,
a non-working day, which could lead to delays.
