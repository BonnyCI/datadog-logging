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
import os
import platform

import pbr.version
import requests

__version__ = pbr.version.VersionInfo('datadog_logging').version_string()

_LOG_LEVEL_ALERT_MAP = {
    logging.DEBUG: "info",
    logging.INFO: "info",
    logging.WARNING: "warning",
    logging.ERROR: "error",
    logging.CRITICAL: "error"
}

DATADOG_HOST = 'https://app.datadoghq.com'

USER_AGENT = 'datadog-logging/%s %s %s/%s' % (
    __version__,
    requests.utils.default_user_agent(),
    platform.python_implementation(),
    platform.python_version()
)


def _create_session(*args, **kwargs):
    # functional testing mock point
    return requests.Session(*args, **kwargs)


class DatadogLogHandler(logging.Handler):

    LOG = logging.getLogger(__name__)

    def __init__(self,
                 tags=None,
                 mentions=None,
                 api_key=None,
                 app_key=None,
                 datadog_host=None,
                 session=None,
                 **kwargs):
        super(DatadogLogHandler, self).__init__(**kwargs)

        self.session = _create_session()

        self.tags = tags
        self.mentions = mentions

        self.api_key = api_key or os.environ.get('DATADOG_API_KEY')
        self.app_key = app_key or os.environ.get('DATADOG_APP_KEY')

        host = datadog_host or os.environ.get('DATADOG_HOST', DATADOG_HOST)
        self.event_api = "%s/api/v1/events" % host.rstrip('/')

        self._api_key_log_once = False
        self._api_failure_log_once = False

    def emit(self, record):
        if not self.api_key:
            if not self._api_key_log_once:
                self._api_key_log_once = True
                self.LOG.warning("Missing Datadog API key. Cannot Use Logger.")

            return

        text = self.format(record)

        if self.mentions is not None:
            text = "\n\n".join([text, " ".join(self.mentions)])

        data = {
            "title": record.getMessage(),
            "text": text
        }

        if self.tags is not None:
            data["tags"] = self.tags

        if record.levelno in _LOG_LEVEL_ALERT_MAP:
            data["alert_type"] = _LOG_LEVEL_ALERT_MAP[record.levelno]

        params = {'api_key': self.api_key}

        if self.app_key:
            params['app_key'] = self.app_key

        headers = {'Content-Type': 'application/json',
                   'User-Agent': USER_AGENT}

        resp = self.session.post(self.event_api,
                                 headers=headers,
                                 json=data,
                                 params=params)

        if (not resp.ok) and (not self._api_failure_log_once):
            self._api_failure_log_once = True
            self.LOG.warning("Failed to post event data: %s", resp.status_code)
