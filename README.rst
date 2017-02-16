===============================
datadog-logging
===============================

Send logging events to datadog

* Free software: Apache license
* Source: https://github.com/BonnyCI/datadog-logging

About
=====

When working with python services we want to be alerted when an error appears in our logs file.
There are plenty of options for this, newrelic_, getsentry_, airbrake_ and hundreds of others, but these seem to have come with the expectation you're doing javascript and websites.
The basic plan of all these services expect you to be sending thousands of events per month.

In our case we don't need this, we expect to send maybe a couple of events per month - but those events are a big deal and we want to know when they happen.
As we already use datadog we want them to end up there and go through our existing reporting channels.

.. _newrelic: https://newrelic.com/
.. _getsentry: https://sentry.io/
.. _airbrake: https://airbrake.io/

History
=======

datadog-logging was completely based upon datadog-logger_.
Unfortunately a side effect of using the datadogpy_ library is that you need to initialize it which means modifying the code of the app you're monitoring.
Ideally we don't want to do this, and a lesson learned from building datadog-builder_ is that for simple commands it is easier (and far easier to test) if you simply make requests against the API.
So we rewrote the handler to pull authentication information directly from the environment so that it can be configured completely via python-logging configuration.

Subsequent to this the library was extended to offer using the dogstatsd_ mechanism of sending events.
If you are already running a datadog agent on this machine it is easier for authentication and prevents having to make blocking web requests from your app if we just send  a local UDP request to dogstatd.

.. _datadog-logger: https://github.com/ustudio/datadog-logger
.. _datadogpy: https://github.com/DataDog/datadogpy
.. _datadog-builder: https://github.com/BonnyCI/datadog-builder
.. _dogstatsd: http://docs.datadoghq.com/guides/dogstatsd/

Handlers
========

There are two handlers present in this package:

 * `datadog_logging.DatadogLogRequestHandler`: A handler that makes a call to the datadog api (over HTTPS) to submit an event.
 * `datadog_logging.DatadogLogStatsdHandler`: A handler that submits the event to dogstatd which can then forward it to datadog.

DatadogLogRequestHandler Options
--------------------------------

`DatadogLogRequestHandler` expects to find in the environment:

 `DATADOG_API_KEY`: The API key to authenticate the request.

and optionally:

 `DATADOG_APP_KEY`: The applictation key to authenticate the request. This is typically not required to send an event but will be used if given.

 `DATADOG_HOST`: An alternative url host to send requests to if required. By default this is the standard API endpoint: `https://app.datadoghq.com`.


DatadogLogStatsdHandler Options
-------------------------------

`DatadogLogStatsdHandler` will work as expected without any configuration, however it will look for the following environment variables:

 `DATADOG_HOST`: The host to send events to. Defaults to localhost.

 `DATADOG_PORT`: The port to send events to. Defaults to 8125.

Configuration
=============

In Python
---------

If you have direct access to the python code you can add the handler directly.

::

    import logging

    import datadog_logging

    logging.basicConfig(level=logging.WARNING)
    logging.addHandler(datadog_logging.DatadogLogRequestHandler(api_key="XYZ"))

Via Configuration
-----------------

What's more interesting for us is being able to configure the handler transparently via `python's file logging`_.
We then add `DATADOG_API_KEY` into the environment before loading our application.

The configuration is similar for the `DatadogStatsdRequestHandler` without needing to set the environment variable.

Example configuration:

::

    [loggers]
    keys=root

    [handlers]
    keys=stream,datadog

    [formatters]
    keys=simple

    [logger_root]
    level=WARNING
    handlers=stream,datadog

    [handler_stream]
    level=DEBUG
    class=StreamHandler
    formatter=simple
    args=(sys.stdout,)

    [handler_datadog]
    level=WARNING
    class=datadog_logging.DatadogLogRequestHandler
    formatter=simple
    args=()

    [formatter_simple]
    format=%(asctime)s %(levelname)s %(name)s: %(message)s
    datefmt=

.. _python's file logging: https://docs.python.org/2/library/logging.config.html
