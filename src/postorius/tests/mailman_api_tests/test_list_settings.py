# -*- coding: utf-8 -*-
# Copyright (C) 2016-2018 by the Free Software Foundation, Inc.
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

"""Tests for list settings"""

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.urls import reverse

from postorius.views.list import SETTINGS_FORMS
from postorius.models import List
from postorius.tests.utils import ViewTestCase


class ListSettingsTest(ViewTestCase):
    """
    Tests for the list settings page.
    """

    def setUp(self):
        super(ListSettingsTest, self).setUp()
        self.domain = self.mm_client.create_domain('example.com')
        self.foo_list = self.domain.create_list('foo')
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'testpass')
        self.superuser = User.objects.create_superuser(
            'testsu', 'su@example.com', 'testpass')
        self.owner = User.objects.create_user(
            'testowner', 'owner@example.com', 'testpass')
        self.moderator = User.objects.create_user(
            'testmoderator', 'moderator@example.com', 'testpass')
        for user in (self.user, self.superuser, self.owner, self.moderator):
            EmailAddress.objects.create(
                user=user, email=user.email, verified=True)
        self.foo_list.add_owner('owner@example.com')
        self.foo_list.add_moderator('moderator@example.com')

    def test_page_not_accessible_if_not_logged_in(self):
        for section_name in SETTINGS_FORMS:
            url = reverse('list_settings', args=('foo.example.com',
                                                 section_name))
            self.assertRedirectsToLogin(url)

    def test_page_not_accessible_for_unprivileged_users(self):
        self.client.login(username='testuser', password='testpass')
        for section_name in SETTINGS_FORMS:
            url = reverse('list_settings', args=('foo.example.com',
                                                 section_name))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    def test_not_accessible_for_moderator(self):
        self.client.login(username='testmoderator', password='testpass')
        for section_name in SETTINGS_FORMS:
            url = reverse('list_settings', args=('foo.example.com',
                                                 section_name))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    def test_page_accessible_for_owner(self):
        self.client.login(username='testowner', password='testpass')
        for section_name in SETTINGS_FORMS:
            url = reverse('list_settings', args=('foo.example.com',
                                                 section_name))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_page_accessible_for_superuser(self):
        self.client.login(username='testsu', password='testpass')
        for section_name in SETTINGS_FORMS:
            url = reverse('list_settings', args=('foo@example.com',
                                                 section_name))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_archiving_policy(self):
        self.assertEqual(self.foo_list.settings['archive_policy'], 'public')
        self.client.login(username='testsu', password='testpass')
        url = reverse('list_settings', args=('foo.example.com', 'archiving'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].initial['archive_policy'], 'public')
        response = self.client.post(url, {'archive_policy': 'private'})
        self.assertRedirects(response, url)
        self.assertHasSuccessMessage(response)
        # Get a new list object to avoid caching
        m_list = List.objects.get(fqdn_listname='foo.example.com')
        self.assertEqual(m_list.settings['archive_policy'], 'private')

    def test_archivers(self):
        self.assertEqual(dict(self.foo_list.archivers),
                         {'mhonarc': True, 'prototype': True,
                          'mail-archive': True})
        self.client.login(username='testsu', password='testpass')
        url = reverse('list_settings', args=('foo.example.com', 'archiving'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial['archivers'],
                         ['mail-archive', 'mhonarc', 'prototype'])
        response = self.client.post(
            url, {'archive_policy': 'public', 'archivers': ['prototype']})
        self.assertRedirects(response, url)
        self.assertHasSuccessMessage(response)
        # Get a new list object to avoid caching
        m_list = List.objects.get(fqdn_listname='foo.example.com')
        self.assertEqual(dict(m_list.archivers),
                         {'mhonarc': False, 'prototype': True,
                          'mail-archive': False})

    def test_bug_117(self):
        self.assertEqual(self.foo_list.settings['first_strip_reply_to'], False)
        self.client.login(username='testsu', password='testpass')
        url = reverse(
            'list_settings', args=('foo.example.com', 'alter_messages'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(
            form.initial['first_strip_reply_to'], False)
        post_data = dict(
            (key, self.foo_list.settings[key])
            for key in form.fields)
        post_data['first_strip_reply_to'] = True
        response = self.client.post(url, post_data)
        self.assertRedirects(response, url)
        self.assertHasSuccessMessage(response)
        # Get a new list object to avoid caching
        m_list = List.objects.get(fqdn_listname='foo.example.com')
        self.assertEqual(m_list.settings['first_strip_reply_to'], True)

    def test_list_identity_allow_empty_prefix_and_desc(self):
        self.assertEqual(self.foo_list.settings['subject_prefix'], '[Foo] ')
        self.assertEqual(self.foo_list.settings['description'], '')
        self.client.login(username='testsu', password='testpass')
        url = reverse('list_settings',
                      args=('foo.example.com', 'list_identity'))
        response = self.client.post(url, {
            'subject_prefix': '',
            'description': '',
            'advertised': 'True',
            })
        self.assertRedirects(response, url)
        self.assertHasSuccessMessage(response)
        # Get a new list object to avoid caching
        m_list = List.objects.get(fqdn_listname='foo.example.com')
        self.assertEqual(m_list.settings['subject_prefix'], '')
        self.assertEqual(m_list.settings['description'], '')

    def test_respond_to_post_requests(self):
        self.assertTrue(self.foo_list.settings['respond_to_post_requests'])
        self.client.login(username='testsu', password='testpass')
        url = reverse('list_settings',
                      args=('foo.example.com', 'automatic_responses'))
        response = self.client.post(
            url,
            {'respond_to_post_requests': False,
             'autorespond_owner': 'none',
             'autorespond_postings': 'none',
             'autorespond_requests': 'none',
             'send_welcome_message': True,
             'autoresponse_grace_period': '20d'})
        self.assertRedirects(response, url)
        self.assertHasSuccessMessage(response)
        mlist = List.objects.get(fqdn_listname='foo.example.com')
        self.assertFalse(mlist.settings['respond_to_post_requests'])

    def test_list_subscription_requests(self):
        self.client.login(username='testowner', password='testpass')
        url = reverse('list_subscription_requests', args=('foo.example.com',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Since there are no pending subscription requests, this page should be
        # empty.
        self.assertContains(response, '<small>(0)</small>')
        self.assertTrue(
            b'There are currently no subscription requests for this list.'
            in response.content)
        self.assertNotContains(response, '<div class="paginator">')
        # Now we set the subscription policy to moderate so that all
        # subscriptions are held for moderator approval.
        self.foo_list.settings['subscription_policy'] = 'moderate'
        self.foo_list.settings.save()
        self.foo_list.subscribe('test@example.com')
        self.foo_list.subscribe('owner@example.com')
        self.foo_list.subscribe('moderator@example.com')
        # Now there should be three subscription requests pending.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for email in ('test@example.com', 'owner@example.com',
                      'moderator@example.com'):
            self.assertTrue(email in str(response.content))
        self.assertContains(response, '<small>(3)</small>')
        # Verify that the list is paginated
        self.assertContains(response, '<div class="paginator">')

    def test_handle_subscription_request(self):
        self.client.login(username='testowner', password='testpass')
        self.foo_list.settings['subscription_policy'] = 'moderate'
        self.foo_list.settings.save()
        self.foo_list.subscribe('test@example.com', pre_verified=True)
        # There should be one pending subscription request.
        self.assertEqual(len(self.foo_list.requests), 1)
        token = self.foo_list.requests[0]['token']
        url = reverse('handle_subscription_request',
                      args=('foo.example.com', token, 'accept'))
        response = self.client.get(url)
        # On success, user is redirected to list_subscription_requests page.
        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url,
                        '/postorius/lists/foo.example.com/subscription_requests')  # noqa
        self.assertEqual(len(self.foo_list.requests), 0)

    def test_remove_all_subscribers(self):
        self.client.login(username='testowner', password='testpass')
        # Let's add 10 subscribers to the list.
        for each in range(10):
            self.foo_list.subscribe('test-{}@example.com'.format(each),
                                    pre_verified=True,
                                    pre_approved=True,
                                    pre_confirmed=True)
        self.assertEqual(len(self.foo_list.members), 10)
        # First lets see the correct form is rendered when we GET
        url = reverse('unsubscribe_all', args=('foo.example.com',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Confirm Removal of All Members' in response.content)
        # If we POST to the above url, we will unsubscribe all the users.
        self.assertEqual(len(self.foo_list.members), 10)
        # Now, let's remove all the subscribers
        self.client.post(url)
        self.assertEqual(len(self.foo_list.members), 0)
