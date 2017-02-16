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

from datadog_logging import version as _version

from datadog_logging.request_handler import *  # noqa
from datadog_logging.statsd_handler import *  # noqa

__version__ = _version.version_string


__all__ = [
    'DATADOG_HOST',
    'DatadogLogRequestHandler',
    'DatadogLogStatsdHandler',
]
