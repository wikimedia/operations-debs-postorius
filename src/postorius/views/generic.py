# -*- coding: utf-8 -*-
# Copyright (C) 1998-2015 by the Free Software Foundation, Inc.
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


from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader, RequestContext
from django.views.generic import TemplateView, View

from postorius.models import (Domain, List, Member, MailmanUser,
                              MailmanApiError, Mailman404Error)
from postorius import utils


class MailmanClientMixin(object):

    """Adds a mailmanclient.Client instance."""

    def client(self):
        if getattr(self, '_client', None) is None:
            self._client = utils.get_client()
        return self._client


class MailingListView(TemplateView, MailmanClientMixin):

    """A generic view for everything based on a mailman.client
    list object.

    Sets self.mailing_list to list object if fqdn_listname in **kwargs.
    """

    def _get_list(self, list_id, page):
        return List.objects.get_or_404(fqdn_listname=list_id)

    def _is_list_owner(self, user, mailing_list):
        if not user.is_authenticated():
            return False
        if user.email in mailing_list.owners:
            return True
        return False

    def _is_list_moderator(self, user, mailing_list):
        if not user.is_authenticated():
            return False
        if user.email in mailing_list.moderators:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        # get the list object.
        if 'list_id' in kwargs:
            try:
                self.mailing_list = self._get_list(kwargs['list_id'],
                                                   int(kwargs.get('page', 1)))
            except MailmanApiError:
                return utils.render_api_error(request)
            request.user.is_list_owner = self._is_list_owner(
                request.user, self.mailing_list)
            request.user.is_list_moderator = self._is_list_moderator(
                request.user, self.mailing_list)
        # set the template
        if 'template' in kwargs:
            self.template = kwargs['template']
        return super(MailingListView, self).dispatch(request, *args, **kwargs)


class MailmanUserView(TemplateView, MailmanClientMixin):

    """A generic view for everything based on a mailman.client
    user object.

    Sets self.mm_user to list object if user_id in **kwargs.
    """

    def _get_first_address(self, user_obj):
        for address in user_obj.addresses:
            return address

    def _get_user(self, user_id):
        try:
            user_obj = MailmanUser.objects.get(address=user_id)
        except Mailman404Error:
            user_obj = None
        # replace display_name with first address if display_name is not set
        if user_obj is not None:
            if (user_obj.display_name == 'None' or
               user_obj.display_name is None):
                user_obj.display_name = ''
            user_obj.first_address = self._get_first_address(user_obj)
        return user_obj

    def _get_list(self, list_id):
        if getattr(self, 'lists', None) is None:
            self.lists = {}
        if self.lists.get(list_id) is None:
            self.lists[list_id] = List.objects.get(fqdn_listname=list_id)
        return self.lists[list_id]

    def _get_memberships(self):
        memberships = []
        if (self.mm_user):
            for m in self.mm_user.subscriptions:
                mlist = m.list_id
                memberships.append(
                    dict(
                        mlist=mlist,
                        role=m.role,
                        preferences=m.preferences,
                        address=m.address))
        return memberships

    def dispatch(self, request, *args, **kwargs):
        # get the user object.
        user_id = None
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
        elif request.user.is_authenticated():
            user_id = request.user.email
        if user_id is not None:
            try:
                self.mm_user = self._get_user(user_id)
            except MailmanApiError:
                return utils.render_api_error(request)

        # set the template
        if 'template' in kwargs:
            self.template = kwargs['template']
        return super(MailmanUserView, self).dispatch(request, *args, **kwargs)
