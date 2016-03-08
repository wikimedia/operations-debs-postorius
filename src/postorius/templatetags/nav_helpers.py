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

from django.core.urlresolvers import reverse
from django import template


register = template.Library()


@register.inclusion_tag('postorius/menu/list_nav.html', takes_context=True)
def list_nav(context, current, title=None):
    if title is None:
        title = ''
    return dict(list=context['list'],
                current=current,
                user=context['request'].user,
                title=title)


@register.inclusion_tag('postorius/menu/mm_user_nav.html', takes_context=True)
def user_nav(context, current, title=None):
    if title is None:
        title = ''
    return dict(mm_user=context['mm_user'],
                current=current,
                user=context['request'].user,
                title=title)


@register.inclusion_tag('postorius/menu/users_nav.html', takes_context=True)
def users_nav(context, current, title=None):
    if title is None:
        title = ''
    return dict(current=current,
                user=context['request'].user,
                title=title)


@register.simple_tag
def page_url(view_name, *args, **kwargs):
    return reverse(view_name, *args, **kwargs)


@register.simple_tag(takes_context=True)
def nav_active_class(context, current, view_name):
    if current == view_name:
        return 'mm_active'
    return ''
