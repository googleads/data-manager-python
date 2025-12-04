Data Manager API utilities and samples for Python
=================================================

Utilities and code samples for working with the Data Manager API and Python.

Requirements
------------
* Python 3.10+

Installation
------------

.. code-block::

  pip install .

Documentation
-------------
Please refer to our `Developer Site`_ for documentation on how to install,
configure, and use this client library.

Run samples
-----------

Samples are provided in the `samples/` directory, and the `samples/sampledata`
directory contains samples of input files you can use with the samples.

To run a sample, invoke the script using the command line. You can pass
arguments to the script in one of two ways:

1. Explicitly, on the command line
-----------------------------------

.. code-block:: bash

   python3 -m samples.events.ingest_events \
     --operating_account_type='GOOGLE_ADS' \
     --operating_account_id='<operating_account_id>' \
     --conversion_action_id='<conversion_action_id>' \
     --json_file='</path/to/your/file>'

2. Using an arguments file
--------------------------

You can also save arguments in a file, with one argument per line.

.. code-block:: text

   --operating_account_type
   GOOGLE_ADS
   --operating_account_id
   <operating_account_id>
   --conversion_action_id
   <conversion_action_id>
   --json_file
   </path/to/your/file>

Then, run the sample by passing the file path, prefixed with the ``@``
character.

.. code-block:: bash

   python3 -m samples.events.ingest_events @/path/to/your/args.txt


Issue tracker
-------------

https://github.com/googleads/data-manager-python/issues

Contributing
------------

Contributions welcome! See the [Contributing Guide](CONTRIBUTING.md).

Authors
-------

* `Josh Radcliff`_

.. _Developer Site: https://developers.google.com/data-manager/api/get-started/set-up-access#python
.. _Josh Radcliff: https://github.com/jradcliff
