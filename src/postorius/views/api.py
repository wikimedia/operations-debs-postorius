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


import re
import sys
import json
import logging


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import (login_required,
                                            permission_required,
                                            user_passes_test)
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader, RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from urllib2 import HTTPError

from postorius import utils
from postorius.models import (Domain, List, Member, MailmanUser,
                              MailmanApiError, Mailman404Error)
from postorius.forms import *
from postorius.auth.decorators import *
from postorius.views.generic import MailingListView, MailmanUserView


logger = logging.getLogger(__name__)


@basic_auth_login
@loggedin_or_403
def api_list_index(request):
    client = utils.get_client()
    res, content = client._connection.call('lists')
    return HttpResponse(json.dumps(content['entries']),
                        content_type="application/json")
