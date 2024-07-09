* Launch the tasks in batches so we don't have to send them to the VLM one by one. In
  the case of Kardex, we'll be dealing with the connection limitations. If we send a
  list of tasks, right now we're closing the connection once we receive a response (Kardex).
  We need to keep listening until all the ids are received, but that locks our thread...
  We also need to respond to operation issues on every task, like full trays, changes
  of quantity, etc... and we can't lock many threads as we could put down the instance.
  Something along the lines of queue_job maybe would need to push to the bus the tasks
  updates (hard?) Or maybe the kardex proxy from c2c where we use a controller to send
  the tasks? This should rely on js, if we want a proper UX.
* Confirming the VLM tasks after the picking is confirmed makes not much sense, but
  we're dealing with the quants limitations. Anyway we shouldn't allow to leave
  operations on halt and after a real VLM task is done, the picking should be validated.
  What to do with the non existing quants (inputs)... maybe we could leave the vlm task
  pending assignation, so when we finally validate the picking we just have to perform
  the proper links.
* Not a requiste right now, but we could need to support batch pickings. Let's deal
  with the basics for now anyway.
