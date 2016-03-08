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

import os
import vcr

from django.conf import settings


TEST_ROOT = os.path.abspath(os.path.dirname(__file__))

FIXTURES_DIR = getattr(
    settings, 'FIXTURES_DIR',
    os.path.join(TEST_ROOT, 'fixtures'))

VCR_RECORD_MODE = os.environ.get(
    'POSTORIUS_VCR_RECORD_MODE',
    getattr(settings, 'VCR_RECORD_MODE', 'once'))

MM_VCR = vcr.VCR(
    cassette_library_dir=os.path.join(FIXTURES_DIR, 'vcr_cassettes'),
    record_mode=VCR_RECORD_MODE)
