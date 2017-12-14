# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017 by the Free Software Foundation, Inc.
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

from __future__ import absolute_import, print_function, unicode_literals

from mock import patch
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.utils.six.moves.urllib.error import HTTPError
from django.test import override_settings

from postorius.tests.utils import ViewTestCase
from postorius.models import MailmanApiError


class ModelTest(ViewTestCase):
    """Tests for the list index page."""

    def setUp(self):
        super(ModelTest, self).setUp()
        self.domain = self.mm_client.create_domain('example.com')
        self.foo_list = self.domain.create_list('foo')

    @override_settings(AUTOCREATE_MAILMAN_USER=False)
    def test_mailman_user_not_created_when_flag_is_off(self):
        user = User.objects.create_user(
            'testuser', 'test@example.com', 'testpass')
        EmailAddress.objects.create(
            user=user, email=user.email, verified=True)
        with self.assertRaises(HTTPError):
            self.mm_client.get_user('test@example.com')

    @override_settings(AUTOCREATE_MAILMAN_USER=True)
    def test_mailman_user_created_when_flag_is_on(self):
        user = User.objects.create_user(
            'testuser', 'test@example.com', 'testpass')
        EmailAddress.objects.create(
            user=user, email=user.email, verified=True)
        mm_user = self.mm_client.get_user('test@example.com')
        self.assertEqual(str(mm_user.addresses[0]), 'test@example.com')

    @override_settings(AUTOCREATE_MAILMAN_USER=True)
    @patch('postorius.models.MailmanUser')
    def test_core_not_reachable(self, mock_model):
        # Fail Gracefully if the Core is not reachable when
        # creating the user account.
        mock_model.objects.create_from_django.side_effect = MailmanApiError
        # User creation should succeed without any error, even though there
        # is no MailmanUser. However, this error should be logged.
        with patch('postorius.models.logger') as log:
            User.objects.create_user('testuser, test@example.com', 'testpass')
            errmsg = 'Mailman Core API is not reachable.'
            log.error.assert_called_with(errmsg)
        # There should be no user in Mailman with this address.
        with self.assertRaises(HTTPError):
            self.mm_client.get_user('test@example.com')
