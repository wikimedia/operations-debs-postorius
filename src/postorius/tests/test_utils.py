# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 by the Free Software Foundation, Inc.
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

"""
.. testsetup::

    >>> from __future__ import absolute_import, unicode_literals

    >>> from postorius.tests.utils import *


Domains
=======

``postorius.tests.utils.create_mock_domain`` creates a mock domain object:

    >>> properties = dict(contact_address='postmaster@example.org',
    ...                   description='Example dot Org',
    ...                   mail_host='example.org',
    ...                   url_host='www.example.org')
    >>> mock_domain = create_mock_domain(properties)
    >>> print mock_domain
    <MagicMock name='Domain' id='...'>
    >>> print mock_domain.contact_address
    postmaster@example.org
    >>> print mock_domain.description
    Example dot Org
    >>> print mock_domain.mail_host
    example.org
    >>> print mock_domain.url_host
    www.example.org


Mailing Lists
=============

``postorius.tests.utils.create_mock_list`` creates a mock list object:

    >>> properties = dict(fqdn_listname='testlist@example.org',
    ...                   mail_host='example.org',
    ...                   list_name='testlist',
    ...                   display_name='Test List')
    >>> mock_list = create_mock_list(properties)
    >>> print mock_list
    <MagicMock name='List' id='...'>
    >>> print mock_list.fqdn_listname
    testlist@example.org
    >>> print mock_list.mail_host
    example.org
    >>> print mock_list.list_name
    testlist
    >>> print mock_list.display_name
    Test List


Memberships
===========

``postorius.tests.utils.create_mock_list`` creates a mock list object:

    >>> properties = dict(fqdn_listname='testlist@example.org',
    ...                   address='les@example.org',)
    >>> mock_member = create_mock_member(properties)
    >>> print mock_member
    <MagicMock name='Member' id='...'>
    >>> print mock_member.fqdn_listname
    testlist@example.org
    >>> print mock_member.address
    les@example.org
"""
