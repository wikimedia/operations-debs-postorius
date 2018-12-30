# -*- coding: utf-8 -*-
# Copyright (C) 1998-2018 by the Free Software Foundation, Inc.
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


from django import template

from postorius.auth.utils import user_is_in_list_roster
from postorius.models import List

from mailmanclient import MailingList

register = template.Library()

__all__ = [
    'get_list',
    'user_is_list_moderator',
    'user_is_list_owner',
]


def get_list(mlist):
    """
    Given either a mailing list identifier or MailingList object itself, return
    the MailingList object. Identifiers could be one of the following:
    - List's posting address: test_list@example.com
    - List's fqdn: test_list.example.com
    """
    return mlist if isinstance(mlist, MailingList) else List.objects.get(mlist)


@register.simple_tag
def user_is_list_owner(user, mlist):
    """
    Given a User object and a MailingList object/identifier, returns True if
    the user is an owner of the given MailingList False otherwise.
    """
    return user_is_in_list_roster(user, get_list(mlist), 'owners')


@register.simple_tag
def user_is_list_moderator(user, mlist):
    """
    Given a User object and a MailingList object/identifier, return True if
    the user is one of the list moderators, False otherwise.
    """
    return user_is_in_list_roster(user, get_list(mlist), 'moderators')
