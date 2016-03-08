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

from mock import patch, MagicMock


def create_mock_domain(properties=None):
    """Create and return a mocked Domain.

    :param properties: A dictionary of the domain's properties.
    :type properties: dict
    :return: A MagicMock object with the properties set.
    :rtype: MagicMock
    """
    mock_object = MagicMock(name='Domain')
    mock_object.base_url = ''
    mock_object.contact_address = ''
    mock_object.description = ''
    mock_object.mail_host = ''
    mock_object.url_host = ''
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
