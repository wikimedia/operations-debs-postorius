# -*- coding: utf-8 -*-
# Copyright (C) 2015-2018 by the Free Software Foundation, Inc.
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


from postorius import utils
from postorius.models import MailmanApiError
from mailmanclient import MailmanConnectionError
import logging

logger = logging.getLogger(__name__)


__all__ = [
    'PostoriusMiddleware',
]


class PostoriusMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, (MailmanApiError, MailmanConnectionError)):
            logger.exception('Mailman REST API not available')
            return utils.render_api_error(request)
