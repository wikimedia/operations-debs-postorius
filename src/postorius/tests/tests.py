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

"""
==============================
Tests Login and Permissions
==============================

Setup Testobject (starts Mailman3 with an empty Database).

    >>> from setup import setup_mm, Testobject, teardown_mm
    >>> testobject = setup_mm(Testobject())

    .. note::
        You need to stop all Mailman3 instances before running the tests

Modules needed
    As we can't make sure that you're running the same language as we did we
    made sure that each test below is executed using the exact same translation
    mechanism as we use to Display you Status Messages and other GUI Texts.

    Import Translation Module to check success messages
        >>> from django.utils.translation import gettext as _

    Import HTTPRedirectObject to check whether a response redirects
        >>> from django.http import HttpResponseRedirect

Import Django test client.

    >>> from django.test.client import Client
    >>> c = Client()


List index
==========

Try accessing the list index page.

    >>> response = c.get('/lists/',)
    >>> response.status_code
    200


Login Required
==================================================

As described within the installation instructions we *already* started using
authentification. The easiest way testing it is that we simply load a page
which is restricted to some users only.
This was done using Django's @login_required Decorator in front of the View.
One of the pages which requires a Login is the Domain Administration, if
we can load the page without a redirect to the Login page, you're either
already logged in or something went wrong.

    >>> response = c.get('/domains/')
    >>> print type(response) == HttpResponseRedirect
    True

=====
Pages
=====

Create a New List
=================

After creating a Domain you should be able to create new Lists. The Button for
doing so is shown on the List index Page which should offer a list of all
available (adverrtised) lists.

    >>> response = c.get('/lists/')
    >>> response.status_code
    200
    >>> "Lists <span>on" in response.content
    True

The new List creation form is opened by clicking on the Button mentioned above
or accessing the page directly

    >>> response = c.get('/lists/new/')
    >>> response.status_code
    200
    >>> print "Create a new List on" in response.content
    True

Creating a new List we do need to specify at least the below mentioned items.
Those were entered using some nice GUI Forms which do only show up available
Values or offer you to choose a name which will be checked during validation.
We're now submitting the form using a POST request and get redirected to
the List Index Page

    >>> response = c.post('/lists/new/',
    ...                   {"listname": "new_list1",
    ...                    "mail_host": "mail.example.com",
    ...                    "list_owner": "james@example.com",
    ...                    "description": "doctest testing list",
    ...                    "advertised": "True",
    ...                    "languages": "English (USA)"})
    >>> print type(response) == HttpResponseRedirect
    True

As List index is an overview of all advertised Lists and we've choosen to
do so we should now see our new List within the overview. HTTP_HOST is added
as META Data for the request because we do only want to see Domains which
belong to the example.com web_host.

    >>> response = c.get('/lists/',HTTP_HOST='example.com')
    >>> response.status_code
    200
    >>> "New_list1" in response.content
    True

List Summary
============

List summary is a dashboard for each List. It does have Links to the most
useful functions which are only related to that Domain. These include the
Values mentioned below. _(function) is used to Translate these to you local
language.

    >>> response = c.get('/lists/new_list1%40mail.example.com/',)
    >>> response.status_code
    200
    >>> _("Subscribe") in response.content
    True
    >>> _("Archives") in response.content
    True
    >>> _("Edit Options") in response.content
    True
    >>> _("Unsubscribe") in response.content
    True

Subscriptions
=============

The Subscriptions form is found on the below URL. Last part of the Url is one
of [None,'subscribe','unsubscribe']

    >>> url = '/subscriptions/new_list1%40mail.example.com/subscribe'
    >>> response = c.get(url)
    >>> response.status_code
    200

Forms will be prefilled with the Users Email if so. is logged in.

    >>> "james@example.com" in response.content
    True

Now we can subscribe James and Katie and check that we get redirected to List
Summary.

    >>> response = c.post(url,
    ...                   {"email": "james@example.com",
    ...                   "real_name": "James Watt",
    ...                   "name": "subscribe",
    ...                   "fqdn_listname": "new_list1@mail.example.com"})
    >>> response = c.post(url,
    ...                   {"email": "katie@example.com",
    ...                   "real_name": "Katie Doe",
    ...                   "name": "subscribe",
    ...                   "fqdn_listname": "new_list1@mail.example.com"})
    >>> print (_('Subscribed')+' katie@example.com') in response.content
    True

The logged in user (james@example.com) can now modify his own membership
using a button which is displayed in list_summary.

    >>> response = c.get('/lists/new_list1%40mail.example.com/')
    >>> "mm_membership" in response.content
    True

Using the same subscription page we can unsubscribe as well.

    >>> response = c.post('/subscriptions/new_list1%40mail.example.com/unsubscribe',
    ...                   {"email": "katie@example.com",
    ...                   "name": "unsubscribe",
    ...                   "fqdn_listname": "new_list1@mail.example.com"})
    >>> print (_('Unsubscribed')+' katie@example.com') in response.content
    True

Mass Subscribe Users (within settings)
======================================

Another page related to Mass Subscriptions will be available to List Owners
as well. This page will allow adding a couple of users to one lists at the
same time.

    >>> url = '/subscriptions/new_list1%40mail.example.com/mass_subscribe/'
    >>> response = c.get(url)
    >>> response.status_code
    200

Try mass subscribing the users 'liza@example.com' and
'george@example.com'. Each address should be provided on a separate
line so add '\\n' between the names to indicate that this was done
(we're on a Linux machine which is why the letter 'n' was used and
the double '\\' instead of a single one is to escape the string
parsing of Python).

    >>> url = '/subscriptions/new_list1%40mail.example.com/mass_subscribe/'
    >>> response = c.post(url,
    ...                   {"emails": "liza@example.com\\ngeorge@example.com"})

If everything was successful, we shall get a positive response from
the page. We'll check that this was the case.

    >>> print _("The mass subscription was successful.") in response.content
    True

Delete the List
===============

Finally, let's delete the list.
We start by checking that the list is really there (for reference).

    >>> response = c.get('/lists/',HTTP_HOST='example.com')
    >>> print "New_list1" in response.content
    True

Trying to delete the List we have to confirm this action
    >>> response = c.get('/delete_list/new_list1%40mail.example.com/',)
    >>> print "Please confirm" in response.content
    True

Confirmed by pressing the button which requests the same page using POST
    >>> response = c.post('/delete_list/new_list1%40mail.example.com/',)

...and check that it's been deleted.
    >>> response = c.get('/lists/',HTTP_HOST='example.com')
    >>> print "new_list1%40example.com" in response.content
    False

==============
Finishing Test
==============

Don't forget to remove the test object after testing all functions
    >>> teardown_mm(testobject)
"""
