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
import uuid

from datadog_logging.tests.unit import base


class SimpleGoodLogs(base.RequestTestCase):

    def setUp(self):
        super(SimpleGoodLogs, self).setUp()
        self.good_mock()

    def test_simple_logging_levels(self):
        logger = self.getRequestLogger(level=logging.WARNING)

        logger.debug('This should not be passed')
        self.assertFalse(self.requests_mock.called)

        logger.warning('This should be passed')
        self.assertTrue(self.requests_mock.called_once)

        self.assertApiKey()

        request_json = self.requests_mock.last_request.json()

        self.assertElement('text', 'This should be passed')
        self.assertElement('title', 'This should be passed')
        self.assertElement('alert_type', 'warning')

    def test_api_key_from_environ(self):
        # unset the one for testing
        self.api_key = None

        api_key = uuid.uuid4().hex

        self.set_env('DATADOG_API_KEY', api_key)

        logger = self.getRequestLogger(level=logging.WARNING)
        logger.warn('ABC')

        self.assertApiKey(api_key)

    def test_app_key_from_environ(self):
        app_key = uuid.uuid4().hex

        self.set_env('DATADOG_APP_KEY', app_key)

        logger = self.getRequestLogger(level=logging.WARNING)
        logger.warn('ABC')

        self.assertQs('app_key', app_key)
