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

import time
import uuid

import fixtures
from requests_mock.contrib import fixture as requests_mock_fixture

import datadog_logging
from datadog_logging.tests import base


class RequestTestCase(base.TestCase):

    EVENT_URL_TMPL = 'https://app.datadoghq.com/event/jump_to?event_id=%s'

    def setUp(self):
        super(RequestTestCase, self).setUp()

        self.api_key = uuid.uuid4().hex
        self.requests_mock = self.useFixture(requests_mock_fixture.Fixture())

    def getRequestLogger(self, **kwargs):
        kwargs.setdefault('api_key', self.api_key)
        return super(RequestTestCase, self).getRequestLogger(uuid.uuid4().hex,
                                                             **kwargs)

    def mock(self, **kwargs):
        datadog_host = kwargs.pop('datadog_host', datadog_logging.DATADOG_HOST)
        event_api = "%s/api/v1/events" % datadog_host.rstrip('/')
        return self.requests_mock.post(event_api, **kwargs)

    def _json_response(self, request, context):
        request_json = request.json()
        event_id = uuid.uuid4().hex

        return {
            'status': 'ok',
            'event': {
                'date_happened': int(time.time()),
                'handle': None,
                'id': event_id,
                'priority': request_json.get('priority', 'normal'),
                'tags': request_json.get('tags', []),
                'text': request_json.get('text'),
                'title': request_json.get('title'),
                'url': self.EVENT_URL_TMPL % event_id,
            }
        }

    def good_mock(self, **kwargs):
        kwargs.setdefault('status_code', 201)
        headers = kwargs.setdefault('headers', {})
        headers.setdefault('Content-Type', 'application/json')
        kwargs.setdefault('json', self._json_response)
        return self.mock(**kwargs)

    def set_env(self, key, val=None):
        return self.useFixture(fixtures.EnvironmentVariable(key, val))

    def assertQs(self, key, val, request=None):
        if not request:
            request = self.requests_mock.last_request

        self.assertEqual([val], request.qs.get(key))

    def assertApiKey(self, api_key=None, request=None):
        if not api_key:
            api_key = self.api_key

        self.assertQs('api_key', api_key, request=request)

    def assertElement(self, key, val, element=None):
        if not element:
            element = self.requests_mock.last_request

        self.assertEqual(val, element.json().get(key))


class _FakeStatsd(object):

    def __init__(self):
        self.history = []

    def event(self, title, text, **kwargs):
        kwargs['title'] = title
        kwargs['text'] = text
        self.history.append(kwargs)


class StatsdTestCase(base.TestCase):

    def setUp(self):
        super(StatsdTestCase, self).setUp()

        self.fake_statsd = _FakeStatsd()

        m = 'datadog_logging.statsd_handler._create_statsd'
        self.useFixture(fixtures.MockPatch(m, self.create_statsd))

    def getStatsdLogger(self, **kwargs):
        return super(StatsdTestCase, self).getStatsdLogger(uuid.uuid4().hex,
                                                           **kwargs)

    @property
    def called_once(self):
        return len(self.fake_statsd.history) == 1

    @property
    def called(self):
        return len(self.fake_statsd.history) > 0

    def create_statsd(self, *args, **kwargs):
        return self.fake_statsd

    def assertElement(self, key, val, event=None):
        if not event:
            event = self.fake_statsd.history[-1]

        self.assertEqual(val, event.get(key))
