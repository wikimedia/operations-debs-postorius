# -*- coding: utf-8 -*-
# Copyright (C) 2012-2018 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.


import os
import vcr
import logging

from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.test import TransactionTestCase
from mock import MagicMock
from six import binary_type, text_type, PY3
from six.moves.urllib_parse import (
    quote, urlparse, urlunparse, parse_qsl, urlencode)
from django_mailman3.lib.mailman import get_mailman_client
from django_mailman3.tests.utils import get_flash_messages


vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)


def get_test_file(*fileparts):
    return os.path.join(os.path.dirname(__file__), "test_data", *fileparts)
get_test_file.__test__ = False  # noqa: E305


def reorder_request_params(request):
    def reorder_params(params):
        parsed = None
        if PY3:
            if isinstance(params, binary_type):
                params = params.decode("ascii")
            parsed = parse_qsl(params, encoding="utf-8")
        else:
            parsed = parse_qsl(params)
        if parsed:
            return urlencode(sorted(parsed, key=lambda kv: kv[0]))
        else:
            # Parsing failed, it may be a simple string.
            return params
        # sort the URL query-string by key names.
    uri_parts = urlparse(request.uri)
    if uri_parts.query:
        request.uri = urlunparse((
            uri_parts.scheme, uri_parts.netloc, uri_parts.path,
            uri_parts.params, reorder_params(uri_parts.query),
            uri_parts.fragment,
        ))
        # convert the request body to text and sort the parameters.
    if isinstance(request.body, binary_type):
        try:
            request._body = request._body.decode('utf-8')
        except UnicodeDecodeError:
            pass
    if isinstance(request.body, text_type):
        request._body = reorder_params(request._body.encode('utf-8'))
    return request


def filter_response_headers(response):
    for header in ('Date', 'Server', 'date', 'server'):
        # The headers are lowercase on Python 2 and capitalized on Python 3
        if header in response['headers']:
            del response['headers'][header]
    return response


def get_vcr(**kwargs):
    # Use the POSTORIUS_VCR_RECORD_MODE environment variable to set the record
    # mode. By default, this value is set to 'once'.
    # See http://vcrpy.readthedocs.io/en/latest/usage.html#record-modes
    # for more details about all the record modes.
    vcr_record_mode = os.getenv('POSTORIUS_VCR_RECORD_MODE', 'once')
    if vcr_record_mode not in ('once', 'all', 'none', 'new_episodes'):
        vcr_log.warning('{} is not a valid VCR.py mode, '
                        'using once as default'.format(vcr_record_mode))
        vcr_record_mode = 'once'

    return vcr.VCR(
        filter_headers=['authorization', 'user-agent', 'date'],
        before_record=reorder_request_params,
        before_record_response=filter_response_headers,
        record_mode=vcr_record_mode,
        **kwargs
    )


def create_mock_domain(properties=None):
    """Create and return a mocked Domain.

    :param properties: A dictionary of the domain's properties.
    :type properties: dict
    :return: A MagicMock object with the properties set.
    :rtype: MagicMock
    """
    mock_object = MagicMock(name='Domain')
    mock_object.contact_address = ''
    mock_object.description = ''
    mock_object.mail_host = ''
    mock_object.lists = []
    if properties is not None:
        for key in properties:
            setattr(mock_object, key, properties[key])
    return mock_object


def create_mock_list(properties=None):
    """Create and return a mocked List.

    :param properties: A dictionary of the list's properties.
    :type properties: dict
    :return: A MagicMock object with the properties set.
    :rtype: MagicMock
    """
    mock_object = MagicMock(name='List')
    mock_object.members = []
    mock_object.moderators = []
    mock_object.owners = []
    # like in mock_domain, some defaults need to be added...
    if properties is not None:
        for key in properties:
            setattr(mock_object, key, properties[key])
    return mock_object


def create_mock_member(properties=None):
    """Create and return a mocked Member.

    :param properties: A dictionary of the member's properties.
    :type properties: dict
    :return: A MagicMock object with the properties set.
    :rtype: MagicMock
    """
    mock_object = MagicMock(name='Member')
    # like in mock_domain, some defaults need to be added...
    if properties is not None:
        for key in properties:
            setattr(mock_object, key, properties[key])
    return mock_object


class ViewTestCase(TransactionTestCase):
    use_vcr = True
    _fixtures_dir = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'fixtures', 'vcr_cassettes')

    _mm_vcr = get_vcr(cassette_library_dir=_fixtures_dir)

    def setUp(self):
        self.mm_client = get_mailman_client()
        if self.use_vcr:
            cm = self._mm_vcr.use_cassette('.'.join([
                self.__class__.__name__, self._testMethodName, 'yaml']))
            self.cassette = cm.__enter__()
            self.addCleanup(cm.__exit__, None, None, None)

    def tearDown(self):
        for d in self.mm_client.domains:
            d.delete()
        for u in self.mm_client.users:
            u.delete()

    def assertHasSuccessMessage(self, response):
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(
            msgs[0].level, messages.SUCCESS,
            "%s: %s" % (messages.DEFAULT_TAGS[msgs[0].level], msgs[0].message))
        return msgs[0].message

    def assertHasErrorMessage(self, response):
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(
            msgs[0].level, messages.ERROR,
            "%s: %s" % (messages.DEFAULT_TAGS[msgs[0].level], msgs[0].message))
        return msgs[0].message

    def assertHasNoMessage(self, response):
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 0)

    def assertRedirectsToLogin(self, url):
        response = self.client.get(url)
        self.assertRedirects(response, '{}?next={}'.format(
            reverse(settings.LOGIN_URL), quote(url)))
