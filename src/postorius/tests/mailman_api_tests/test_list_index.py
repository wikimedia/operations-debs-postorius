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


from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.urls import reverse

from postorius.tests.utils import ViewTestCase


class ListIndexPageTest(ViewTestCase):
    """Tests for the list index page."""

    def setUp(self):
        super(ListIndexPageTest, self).setUp()
        self.domain = self.mm_client.create_domain('example.com')
        self.foo_list = self.domain.create_list('foo')
        self.bar_list = self.domain.create_list('bar')

        self.user = User.objects.create_user('user', 'user@example.com', 'pwd')
        self.superuser = User.objects.create_superuser(
            'su', 'su@example.com', 'pwd')

        for user in (self.user, self.superuser):
            EmailAddress.objects.create(
                user=user, email=user.email, verified=True)

    def test_list_index_contains_the_lists(self):
        # The list index page should contain the lists
        response = self.client.get(reverse('list_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 2)
        # The lists should be sorted by address
        self.assertEqual([l.fqdn_listname for l in response.context['lists']],
                         ['bar@example.com', 'foo@example.com'])

    def test_list_index_only_contains_advertised_lists(self):
        # The list index page should contain only contain the advertised lists
        baz_list = self.domain.create_list('baz')
        baz_list.settings['advertised'] = False
        baz_list.settings.save()
        response = self.client.get(reverse('list_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 2)
        self.assertNotIn(
            'baz.example.com',
            [ml.list_id for ml in response.context['lists']])

    def test_list_index_post_redirects(self):
        response = self.client.post(reverse('list_index'),
                                    dict(list='foo.example.com'))
        # This should redirect to the list's summary view.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/postorius/lists/foo.example.com/')

    def test_list_index_unadvertized(self):
        # Test that superuser can see unadvertized lists.
        baz_list = self.domain.create_list('baz')
        baz_list.settings['advertised'] = False
        baz_list.settings.save()
        # Superuser should be able to see all lists.
        self.client.login(username='su', password='pwd')
        url = reverse('list_index') + '?all-lists'
        response = self.client.get(url)
        self.assertEqual(len(response.context['lists']), 3)
        self.assertTrue(
            b'Only admins see unadvertised lists in the list index.' in
            response.content)

    def test_list_index_all_lists(self):
        # Test that list index page for a logged-in user.
        self.client.login(username='user', password='pwd')
        url = reverse('list_index')
        response = self.client.get(url)
        # Since this user isn't related to any list, their index page will
        # redirect to all-lists.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/postorius/lists/?all-lists')
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 2)
        # Now, if we subscribe the user to a list, it will show only that list.
        self.foo_list.subscribe(
            self.user.email, pre_confirmed=True, pre_verified=True)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 1)
        # List that you are owners and moderators for should also show up.
        self.bar_list.add_owner(self.user.email)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 2)

    def test_list_index_owner_only(self):
        # Test that filtering by list-owner role works.
        self.client.login(username='user', password='pwd')
        url = reverse('list_index')
        response = self.client.get(url + '?role=owner')
        # Current user is not an owner of any list.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 0)
        # Let's make them an owner of a list and see if it shows up.
        self.foo_list.add_owner(self.user.email)
        response = self.client.get(url + '?role=owner')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 1)
        # Test all lists are available on all-list page.
        response = self.client.get(url + '?all-lists')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 2)

    def test_list_index_moderator_only(self):
        # Test that filtering by list-moderator role works.
        self.client.login(username='user', password='pwd')
        url = reverse('list_index')
        response = self.client.get(url + '?role=moderator')
        # Current user is not an owner of any list.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 0)
        # Let's make them an moderator of a list and see if it shows up.
        self.foo_list.add_moderator(self.user.email)
        response = self.client.get(url + '?role=moderator')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 1)
        # Test all lists are available on all-list page.
        response = self.client.get(url + '?all-lists')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 2)

    def test_list_index_subscriber_only(self):
        # Test that filtering by list-moderator role works.
        self.client.login(username='user', password='pwd')
        url = reverse('list_index')
        response = self.client.get(url + '?role=member')
        # Current user is not an owner of any list.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 0)
        # Let's make them an moderator of a list and see if it shows up.
        self.foo_list.subscribe(
            self.user.email, pre_confirmed=True, pre_verified=True)
        response = self.client.get(url + '?role=member')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 1)
        # Test all lists are available on all-list page.
        response = self.client.get(url + '?all-lists')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['lists']), 2)

    def test_list_index_multiple_roles(self):
        # Test that filtering by list-moderator role works.
        self.client.login(username='user', password='pwd')
        url = reverse('list_index')
        # Current user is not an owner of any list.
        self.foo_list.subscribe(
            self.user.email, pre_confirmed=True, pre_verified=True)
        self.foo_list.add_owner(self.user.email)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Make sure that lists aren't repeated if the user has multiple roles
        # in the same mailing list.
        self.assertEqual(len(response.context['lists']), 1)

    def test_list_index_multiple_addresses(self):
        EmailAddress.objects.create(
            user=self.user, email='test-email2@example.com', verified=True)
        self.foo_list.subscribe(
            'test-email2@example.com', pre_confirmed=True, pre_verified=True)
        self.client.login(username='user', password='pwd')
        url = reverse('list_index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Make sure that memberships of other email addresses than primary one
        # showup here.
        self.assertEqual(len(response.context['lists']), 1)
