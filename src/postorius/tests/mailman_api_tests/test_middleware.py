# -*- coding: utf-8 -*-
# Copyright (C) 2017 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import, unicode_literals

import mock
try:
    # For django 1.10+
    from django.urls import reverse
except ImportError:
    # For django < 1.10
    from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from postorius.models import MailmanApiError
from mailmanclient import MailmanConnectionError


class TestMiddleware(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    @mock.patch('postorius.views.list.list_index')
    def test_middleware_request(self, mock_method):
        # Mock the view function to raise MailmanApiError and verify
        # the behavior of the middleware function.
        mock_method.side_effect = MailmanApiError
        response = self.client.get(reverse('list_index'))
        # Check that correct error page is rendered.
        self.assertTrue('Mailman REST API not available' in response.content)
        mock_method.reset_mock()
        # Check similar semantics with MailmanConnectionError from
        # mailmanclient.
        mock_method.side_effect = MailmanConnectionError
        response = self.client.get(reverse('list_index'))
        self.assertTrue('Mailman REST API not available' in response.content)
