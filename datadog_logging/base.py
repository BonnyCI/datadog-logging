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


LOG_LEVEL_ALERT_MAP = {
    logging.DEBUG: "info",
    logging.INFO: "info",
    logging.WARNING: "warning",
    logging.ERROR: "error",
    logging.CRITICAL: "error"
}


class DatadogLogBaseHandler(logging.Handler):

    def __init__(self, tags=None, mentions=None, **kwargs):
        super(DatadogLogBaseHandler, self).__init__(**kwargs)

        self.tags = tags
        self.mentions = mentions

    def emit(self, record):
        text = self.format(record)

        if self.mentions is not None:
            text = '\n\n'.join([text, ' '.join(self.mentions)])

        data = {
            'title': record.getMessage(),
            'text': text
        }

        if self.tags is not None:
            data['tags'] = self.tags

        if record.levelno in LOG_LEVEL_ALERT_MAP:
            data['alert_type'] = LOG_LEVEL_ALERT_MAP[record.levelno]

        self.send_event(**data)

    def send_event(self,
                   title=None,
                   text=None,
                   alert_type=None,
                   aggregation_key=None,
                   source_type_name=None,
                   date_happened=None,
                   priority=None,
                   tags=None,
                   hostname=None):
        raise NotImplementedError()
