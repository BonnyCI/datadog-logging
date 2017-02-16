# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from datadog.dogstatsd import DogStatsd

from datadog_logging import base


__all__ = ('DatadogLogStatsdHandler',)


def _create_statsd(*args, **kwargs):
    # testing mock point
    return DogStatsd(*args, **kwargs)


class DatadogLogStatsdHandler(base.DatadogLogBaseHandler):

    LOG = logging.getLogger(__name__)

    def __init__(self,
                 host='localhost',
                 port=8125,
                 **kwargs):
        super(DatadogLogStatsdHandler, self).__init__(**kwargs)
        self.statsd = _create_statsd(host=host, port=port)

    def send_event(self,
                   title,
                   text,
                   alert_type=None,
                   aggregation_key=None,
                   source_type_name=None,
                   date_happened=None,
                   priority=None,
                   tags=None,
                   hostname=None):
        self.statsd.event(title,
                          text,
                          alert_type=alert_type,
                          aggregation_key=aggregation_key,
                          source_type_name=source_type_name,
                          date_happened=date_happened,
                          priority=priority,
                          tags=tags,
                          hostname=hostname)
