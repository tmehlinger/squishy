Changelog
=========

0.1.0
-----

**BREAKING CHANGES**
* The consumer now dispatches an ``SQS.Message`` instance to the callback instead of dictionary.

Bug fixes:
* Fixed a bug in the multiprocessing workers where they would iterate infinitely if the callback raised an exception. (Travis Mehlinger)

New features:
* Squishy now has unit tests!

0.0.3
-----

Bug fixes:
* Fixed relative imports for modules that have the same name as a package. (Alejandro Mesa)
* Fixed missing import for gevent.monkey. (Alejandro Mesa)
* Fixed a bug with passing the message to the worker process without unpacking the dictionary. (Alejandro Mesa)
* Fixed a bug where the worker would fail to handle keyboard interrupts. (Alejandro Mesa)
* Fixed a bug with deleting keys from the results_to_message list while iterating through the list. (Alejandro Mesa)

0.0.2
-----

Bug fixes:
* Switched to RST to be PyPI-friendly.


0.0.1
-----

* First release.
