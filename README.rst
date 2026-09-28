Data Manager API utility library and samples for Python
=======================================================

|pypi|

Utility library and code samples for working with the
`Data Manager API <https://developers.google.com/data-manager/api>`_ and Python.

Requirements
------------

* Python 3.10+

Setup instructions
------------------

The ``google-ads-datamanager-util`` utility library is published to `PyPI`_.
Install it using ``pip``:

.. code-block:: bash

  pip install google-ads-datamanager-util

For complete instructions on setting up API access and installing the client and
utility libraries, see the `Set up API access`_ and `Install a client library`_
guides.

Repository structure
--------------------

* `src/ <src/>`_: Source code for the ``google-ads-datamanager-util`` PyPI
  package. Use the utilities in the library to help with common tasks like
  formatting, hashing, encrypting, and encoding data for Data Manager API
  requests.
* `samples/ <samples/>`_: Code samples demonstrating how to construct and send
  requests to the Data Manager API using the `google-ads-datamanager`_ client
  library and the ``google-ads-datamanager-util`` utility library.

Run samples
-----------

Samples are provided in the ``samples/`` directory, and the ``samples/sampledata``
directory contains samples of input files you can use with the samples.

To run a sample, first install the sample dependencies:

.. code-block:: bash

   pip install -r samples/requirements.txt

Then invoke the sample script using the command line. You can pass
arguments to the script in one of two ways:

1. Explicitly, on the command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python3 samples/events/ingest_events.py \
     --operating_account_type='GOOGLE_ADS' \
     --operating_account_id='<operating_account_id>' \
     --conversion_action_id='<conversion_action_id>' \
     --json_file='</path/to/your/file>'

2. Using an arguments file
~~~~~~~~~~~~~~~~~~~~~~~~~~

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

   python3 samples/events/ingest_events.py @/path/to/your/args.txt


Issue tracker
-------------

* https://github.com/googleads/data-manager-python/issues

Contributing
------------

Contributions welcome! See the `Contributing Guide <CONTRIBUTING.md>`_.

Authors
-------

* `Josh Radcliff`_
* `Lindsey Volta`_

.. |pypi| image:: https://img.shields.io/pypi/v/google-ads-datamanager-util.svg
   :target: https://pypi.org/project/google-ads-datamanager-util/
   :alt: PyPI version
.. _PyPI: https://pypi.org/project/google-ads-datamanager-util/
.. _Set up API access: https://developers.google.com/data-manager/api/devguides/quickstart/set-up-access
.. _Install a client library: https://developers.google.com/data-manager/api/devguides/quickstart/install-library#python
.. _google-ads-datamanager: https://pypi.org/project/google-ads-datamanager/
.. _Josh Radcliff: https://github.com/jradcliff
.. _Lindsey Volta: https://github.com/lindsey-volta
