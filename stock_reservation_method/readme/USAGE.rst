You can configure on picking operation types one of this methods
  * **At confirmation** (*When a pick is confirmed, the reservation is made immediately*, **default**)
  * **Manually** (*You have to make a manual inventory reservation, it is not reserved when confirming the picking*)
  * **Before Scheduled Date** (*This will be reserved based on the date calculated with the configuration of days in the type of operation, depending on the priority of the stock movement, if it has maximum priority (1), the 'reservation_days_before_priority' field will be used, otherwise the field 'reservation_days_before'*)
