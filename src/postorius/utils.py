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


import logging

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import gettext as _
from mailmanclient import Client


logger = logging.getLogger(__name__)


def render_api_error(request):
    """Renders an error template.
    Use if MailmanApiError is catched.
    """
    return render(request, 'postorius/errors/generic.html',
                  {'error': _('Mailman REST API not available. Please start Mailman core.')},   # noqa: E501
                  status=503)


def get_mailman_client():
    # easier to patch during unit tests
    client = Client(
        '%s/3.1' %
        settings.MAILMAN_REST_API_URL,
        settings.MAILMAN_REST_API_USER,
        settings.MAILMAN_REST_API_PASS)
    return client


LANGUAGES = (
    ('ar', 'Arabic'),
    ('ast', 'Asturian'),
    ('ca', 'Catalan'),
    ('cs', 'Czech'),
    ('da', 'Danish'),
    ('de', 'German'),
    ('el', 'Greek'),
    ('es', 'Spanish'),
    ('et', 'Estonian'),
    ('eu', 'Euskara'),
    ('fi', 'Finnish'),
    ('fr', 'French'),
    ('gl', 'Galician'),
    ('he', 'Hebrew'),
    ('hr', 'Croatian'),
    ('hu', 'Hungarian'),
    ('ia', 'Interlingua'),
    ('it', 'Italian'),
    ('ja', 'Japanese'),
    ('ko', 'Korean'),
    ('lt', 'Lithuanian'),
    ('nl', 'Dutch'),
    ('no', 'Norwegian'),
    ('pl', 'Polish'),
    ('pt', 'Protuguese'),
    ('pt_BR', 'Protuguese (Brazil)'),
    ('ro', 'Romanian'),
    ('ru', 'Russian'),
    ('sk', 'Slovak'),
    ('sl', 'Slovenian'),
    ('sr', 'Serbian'),
    ('sv', 'Swedish'),
    ('tr', 'Turkish'),
    ('uk', 'Ukrainian'),
    ('vi', 'Vietnamese'),
    ('zh_CN', 'Chinese'),
    ('zh_TW', 'Chinese (Taiwan)'),
    ('en', 'English (USA)'),
)
