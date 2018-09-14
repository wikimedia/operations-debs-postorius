# -*- coding: utf-8 -*-
# Copyright (C) 2017-2018 by the Free Software Foundation, Inc.
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
#

import re
from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django_mailman3.lib.mailman import get_mailman_client

from postorius.forms.fields import ListOfStringsField


ACTION_CHOICES = (
    ("hold", _("Hold for moderation")),
    ("reject", _("Reject (with notification)")),
    ("discard", _("Discard (no notification)")),
    ("accept", _("Accept immediately (bypass other rules)")),
    ("defer", _("Default processing")),
)


EMPTY_STRING = ''


class ListNew(forms.Form):

    """
    Form fields to add a new list. Languages are hard coded which should
    be replaced by a REST lookup of available languages.
    """
    listname = forms.CharField(
        label=_('List Name'),
        required=True,
        error_messages={'required': _('Please enter a name for your list.'),
                        'invalid': _('Please enter a valid list name.')})
    mail_host = forms.ChoiceField()
    list_owner = forms.EmailField(
        label=_('Initial list owner address'),
        error_messages={
            'required': _("Please enter the list owner's email address.")},
        required=True)
    advertised = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label=_('Advertise this list?'),
        error_messages={
            'required': _("Please choose a list type.")},
        required=True,
        choices=(
            (True, _("Advertise this list in list index")),
            (False, _("Hide this list in list index"))))
    list_style = forms.ChoiceField()
    description = forms.CharField(
        label=_('Description'),
        required=False)

    def __init__(self, domain_choices, style_choices, *args, **kwargs):
        super(ListNew, self).__init__(*args, **kwargs)
        self.fields["mail_host"] = forms.ChoiceField(
            widget=forms.Select(),
            label=_('Mail Host'),
            required=True,
            choices=domain_choices,
            error_messages={'required': _("Choose an existing Domain."),
                            'invalid': _("Choose a valid Mail Host")})
        self.fields["list_style"] = forms.ChoiceField(
            widget=forms.Select(),
            label=_('List Style'),
            required=True,
            choices=style_choices,
            error_messages={'required': _("Choose a List Style."),
                            'invalid': _("Choose a valid List Style.")})
        if len(domain_choices) < 2:
            self.fields["mail_host"].help_text = _(
                "Site admin has not created any domains")
            # if len(choices) < 2:
            #    help_text=_("No domains available: " +
            #                "The site admin must create new domains " +
            #                "before you will be able to create a list")

    def clean_listname(self):
        try:
            validate_email(self.cleaned_data['listname'] + '@example.net')
        except ValidationError:
            # TODO (maxking): Error should atleast point to what is a valid
            # listname. It may not always be obvious which characters aren't
            # allowed in a listname.
            raise forms.ValidationError(_("Please enter a valid listname"))
        return self.cleaned_data['listname']

    class Meta:

        """
        Class to handle the automatic insertion of fieldsets and divs.

        To use it: add a list for each wished fieldset. The first item in
        the list should be the wished name of the fieldset, the following
        the fields that should be included in the fieldset.
        """
        layout = [["List Details",
                   "listname",
                   "mail_host",
                   "list_style",
                   "list_owner",
                   "description",
                   "advertised"], ]


class ListSubscribe(forms.Form):
    """Form fields to join an existing list.
    """

    email = forms.ChoiceField(
        label=_('Your email address'),
        validators=[validate_email],
        widget=forms.Select(),
        error_messages={
            'required': _('Please enter an email address.'),
            'invalid': _('Please enter a valid email address.')})

    display_name = forms.CharField(
        label=_('Your name (optional)'), required=False)

    def __init__(self, user_emails, *args, **kwargs):
        super(ListSubscribe, self).__init__(*args, **kwargs)
        self.fields['email'].choices = ((address, address)
                                        for address in user_emails)


class ListAnonymousSubscribe(forms.Form):
    """Form fields to join an existing list as an anonymous user.
    """

    email = forms.CharField(
        label=_('Your email address'),
        validators=[validate_email],
        error_messages={
            'required': _('Please enter an email address.'),
            'invalid': _('Please enter a valid email address.')})

    display_name = forms.CharField(
        label=_('Your name (optional)'), required=False)


class ListSettingsForm(forms.Form):
    """
    Base class for list settings forms.
    """
    mlist_properties = []

    def __init__(self, *args, **kwargs):
        self._mlist = kwargs.pop('mlist')
        super(ListSettingsForm, self).__init__(*args, **kwargs)


SUBSCRIPTION_POLICY_CHOICES = (
    ('open', _('Open')),
    ('confirm', _('Confirm')),
    ('moderate', _('Moderate')),
    ('confirm_then_moderate', _('Confirm, then moderate')),
)


class ListSubscriptionPolicyForm(ListSettingsForm):
    """
    List subscription policy settings.
    """
    subscription_policy = forms.ChoiceField(
        label=_('Subscription Policy'),
        choices=SUBSCRIPTION_POLICY_CHOICES,
        help_text=_('Open: Subscriptions are added automatically\n'
                    'Confirm: Subscribers need to confirm the subscription '
                    'using an email sent to them\n'
                    'Moderate: Moderators will have to authorize '
                    'each subscription manually.\n'
                    'Confirm then Moderate: First subscribers have to confirm,'
                    ' then a moderator '
                    'needs to authorize.'))


class ArchiveSettingsForm(ListSettingsForm):
    """
    Set the general archive policy.
    """
    mlist_properties = ['archivers']

    archive_policy_choices = (
        ("public", _("Public archives")),
        ("private", _("Private archives")),
        ("never", _("Do not archive this list")),
    )

    archive_policy = forms.ChoiceField(
        choices=archive_policy_choices,
        widget=forms.RadioSelect,
        label=_('Archive policy'),
        help_text=_('Policy for archiving messages for this list'),
    )

    archivers = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label=_('Active archivers'),
        required=False)  # May be empty if no archivers are desired.

    def __init__(self, *args, **kwargs):
        super(ArchiveSettingsForm, self).__init__(*args, **kwargs)
        archiver_opts = sorted(self._mlist.archivers.keys())
        self.fields['archivers'].choices = sorted(
            [(key, key) for key in archiver_opts])
        if self.initial:
            self.initial['archivers'] = [
                key for key in archiver_opts if self._mlist.archivers[key] is True]   # noqa

    def clean_archivers(self):
        result = {}
        for archiver, etc in self.fields['archivers'].choices:
            result[archiver] = archiver in self.cleaned_data['archivers']
        self.cleaned_data['archivers'] = result
        return result


class MessageAcceptanceForm(ListSettingsForm):
    """
    List messages acceptance settings.
    """
    acceptable_aliases = ListOfStringsField(
        label=_("Acceptable aliases"),
        required=False,
        help_text=_(
            'This is a list, one per line, of addresses and regexps matching '
            'addresses that are acceptable in To: or Cc: in lieu of the list '
            'posting address when `require_explicit_destination\' is enabled. '
            ' Entries are either email addresses or regexps matching email '
            'addresses.  Regexps are entries beginning with `^\' and are '
            'matched against every recipient address in the message. The '
            'matching is performed with Python\'s re.match() function, meaning'
            ' they are anchored to the start of the string.'))
    require_explicit_destination = forms.BooleanField(
        widget=forms.RadioSelect(choices=((True, _('Yes')), (False, _('No')))),
        required=False,
        label=_('Require Explicit Destination'),
        help_text=_(
            'This checks to ensure that the list posting address or an '
            'acceptable alias explicitly appears in a To: or Cc: header in '
            'the post.'))
    administrivia = forms.BooleanField(
        widget=forms.RadioSelect(choices=((True, _('Yes')), (False, _('No')))),
        required=False,
        label=_('Administrivia'),
        help_text=_(
            'Administrivia tests will check postings to see whether it\'s '
            'really meant as an administrative request (like subscribe, '
            'unsubscribe, etc), and will add it to the the administrative '
            'requests queue, notifying the administrator of the new request, '
            'in the process.'))
    default_member_action = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label=_('Default action to take when a member posts to the list'),
        error_messages={
            'required': _("Please choose a default member action.")},
        required=True,
        choices=ACTION_CHOICES,
        help_text=_(
            'Default action to take when a member posts to the list.\n'
            'Hold: This holds the message for approval by the list '
            'moderators.\n'
            'Reject: this automatically rejects the message by sending a '
            'bounce notice to the post\'s author. The text of the bounce '
            'notice can be configured by you.\n'
            'Discard: this simply discards the message, with no notice '
            'sent to the post\'s author.\n'
            'Accept: accepts any postings without any further checks.\n'
            'Default Processing: run additional checks and accept '
            'the message.'))
    default_nonmember_action = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label=_('Default action to take when a non-member posts to the'
                'list'),
        error_messages={
            'required': _("Please choose a default non-member action.")},
        required=True,
        choices=ACTION_CHOICES,
        help_text=_(
            'When a post from a non-member is received, the message\'s sender '
            'is matched against the list of explicitly accepted, held, '
            'rejected (bounced), and discarded addresses. '
            'If no match is found, then this action is taken.'))
    max_message_size = forms.IntegerField(
        min_value=0,
        label=_('Maximum message size'),
        required=False,
        help_text=_(
            'The maximum allowed message size. '
            'This can be used to prevent emails with large attachments. '
            'A size of 0 disables the check.'))

    def clean_acceptable_aliases(self):
        # python's urlencode will drop this attribute completely if an empty
        # list is passed with doseq=True. To make it work for us, we instead
        # use an empty string to signify an empty value. In turn, Core will
        # also consider an empty value to be empty list for list-of-strings
        # field.
        if not self.cleaned_data['acceptable_aliases']:
            return EMPTY_STRING
        for alias in self.cleaned_data['acceptable_aliases']:
            if alias.startswith('^'):
                try:
                    re.compile(alias)
                except re.error as e:
                    raise forms.ValidationError(
                        _('Invalid alias regexp: {}: {}').format(alias, e.msg))
            else:
                try:
                    validate_email(alias)
                except ValidationError:
                    raise forms.ValidationError(
                        _('Invalid alias email: {}').format(alias))
        return self.cleaned_data['acceptable_aliases']


class DigestSettingsForm(ListSettingsForm):
    """
    List digest settings.
    """
    digest_size_threshold = forms.DecimalField(
        label=_('Digest size threshold'),
        help_text=_('How big in Kb should a digest be before '
                    'it gets sent out?'))


class DMARCMitigationsForm(ListSettingsForm):
    """
    DMARC Mitigations list settings.
    """
    dmarc_mitigate_action = forms.ChoiceField(
        label=_('DMARC mitigation action'),
        widget=forms.Select(),
        required=False,
        error_messages={
            'required': _("Please choose a DMARC mitigation action.")},
        choices=(
            ('no_mitigation', _('No DMARC mitigations')),
            ('munge_from', _('Replace From: with list address')),
            ('wrap_message',
             _('Wrap the message in an outer message From: the list.')),
            ('reject', _('Reject the message')),
            ('discard', _('Discard the message'))),
        help_text=_(
            'The action to apply to messages From: a domain publishing a '
            'DMARC policy of reject or quarantine or to all messages if '
            'DMARC Mitigate unconditionally is True.'))
    dmarc_mitigate_unconditionally = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('DMARC Mitigate unconditionally'),
        help_text=_(
            'If DMARC mitigation action is munge_from or wrap_message, '
            'should it apply to all messages regardless of the DMARC policy '
            'of the From: domain.'))
    dmarc_moderation_notice = forms.CharField(
        label=_('DMARC rejection notice'),
        required=False,
        widget=forms.Textarea(),
        help_text=_(
            'Text to replace the default reason in any rejection notice to '
            'be sent when DMARC mitigation action of reject applies.'))
    dmarc_wrapped_message_text = forms.CharField(
        label=_('DMARC wrapped message text'),
        required=False,
        widget=forms.Textarea(),
        help_text=_(
            'Text to be added as a separate text/plain MIME part preceding '
            'the original message part in the wrapped message when DMARC '
            'mitigation action of wrap message applies.'))


class AlterMessagesForm(ListSettingsForm):
    """
    Alter messages list settings.
    """
    filter_content = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Filter content'),
        help_text=_('Should Mailman filter the content of list traffic '
                    'according to the settings below?'))
    collapse_alternatives = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Collapse alternatives'),
        help_text=_('Should Mailman collapse multipart/alternative to '
                    'its first part content?'))
    convert_html_to_plaintext = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Convert html to plaintext'),
        help_text=_('Should Mailman convert text/html parts to plain text? '
                    'This conversion happens after MIME attachments '
                    'have been stripped.'))
    anonymous_list = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Anonymous list'),
        help_text=_('Hide the sender of a message, '
                    'replacing it with the list address '
                    '(Removes From, Sender and Reply-To fields)'))
    include_rfc2369_headers = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Include RFC2369 headers'),
        help_text=_(
            'Yes is highly recommended. RFC 2369 defines a set of List-* '
            'headers that are normally added to every message sent to the '
            'list membership. These greatly aid end-users who are using '
            'standards compliant mail readers. They should normally always '
            'be enabled. However, not all mail readers are standards '
            'compliant yet, and if you have a large number of members who are '
            'using non-compliant mail readers, they may be annoyed at these '
            'headers. You should first try to educate your members as to why '
            'these headers exist, and how to hide them in their mail clients. '
            'As a last resort you can disable these headers, but this is not '
            'recommended (and in fact, your ability to disable these headers '
            'may eventually go away).'))
    allow_list_posts = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_("Include the list post header"),
        help_text=_(
            "This can be set to no for announce lists that do not wish to "
            "include the List-Post header because posting to the list is "
            "discouraged."))
    reply_to_address = forms.CharField(
        label=_('Explicit reply-to address'),
        required=False,
        help_text=_(
            'This option allows admins to set an explicit Reply-to address. '
            'It is only used if the reply-to is set to use an explicitly set '
            'header'))
    first_strip_reply_to = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        help_text=_(
            'Should any existing Reply-To: header found in the original '
            'message be stripped? If so, this will be done regardless of '
            'whether an explict Reply-To: header is added by Mailman or not.'))
    reply_goes_to_list = forms.ChoiceField(
        label=_('Reply goes to list'),
        widget=forms.Select(),
        required=False,
        error_messages={
            'required': _("Please choose a reply-to action.")},
        choices=(
            ('no_munging', _('No Munging')),
            ('point_to_list', _('Reply goes to list')),
            ('explicit_header', _('Explicit Reply-to header set'))),
        help_text=_(
            'Where are replies to list messages directed? No Munging is '
            'strongly recommended for most mailing lists. \nThis option '
            'controls what Mailman does to the Reply-To: header in messages '
            'flowing through this mailing list. When set to No Munging, no '
            'Reply-To: header is '
            'added by Mailman, although if one is present in the original '
            'message, it is not stripped. Setting this value to either Reply '
            'to List or Explicit Reply causes Mailman to insert a specific '
            'Reply-To: header in all messages, overriding the header in the '
            'original message if necessary (Explicit Reply inserts the value '
            'of reply_to_address). There are many reasons not to introduce or '
            'override the Reply-To: header. One is that some posters depend '
            'on their own Reply-To: settings to convey their valid return '
            'address. Another is that modifying Reply-To: makes it much more '
            'difficult to send private replies. See `Reply-To\' Munging '
            'Considered Harmful for a general discussion of this issue. '
            'See Reply-To Munging Considered Useful for a dissenting opinion. '
            'Some mailing lists have restricted '
            'posting privileges, with a parallel list devoted to discussions. '
            'Examples are `patches\' or `checkin\' lists, where software '
            'changes are posted by a revision control system, but discussion '
            'about the changes occurs on a developers mailing list. To '
            'support these types of mailing lists, select Explicit Reply and '
            'set the Reply-To: address option to point to the parallel list.'))
    posting_pipeline = forms.ChoiceField(
        label=_('Pipeline'),
        widget=forms.Select(),
        required=False,
        choices=lambda: ((p, p) for p in get_mailman_client()
                         .pipelines['pipelines']),
        help_text=_('Type of pipeline you want to use for this mailing list'))


class ListAutomaticResponsesForm(ListSettingsForm):
    """
    List settings for automatic responses.
    """
    autorespond_choices = (
        ("respond_and_continue", _("Respond and continue processing")),
        ("respond_and_discard", _("Respond and discard message")),
        ("none", _("No automatic response")))
    autorespond_owner = forms.ChoiceField(
        choices=autorespond_choices,
        widget=forms.RadioSelect,
        label=_('Autorespond to list owner'),
        help_text=_('Should Mailman send an auto-response to '
                    'emails sent to the -owner address?'))
    autoresponse_owner_text = forms.CharField(
        label=_('Autoresponse owner text'),
        widget=forms.Textarea(),
        required=False,
        help_text=_('Auto-response text to send to -owner emails.'))
    autorespond_postings = forms.ChoiceField(
        choices=autorespond_choices,
        widget=forms.RadioSelect,
        label=_('Autorespond postings'),
        help_text=_('Should Mailman send an auto-response to '
                    'mailing list posters?'))
    autoresponse_postings_text = forms.CharField(
        label=_('Autoresponse postings text'),
        widget=forms.Textarea(),
        required=False,
        help_text=_('Auto-response text to send to mailing list posters.'))
    autorespond_requests = forms.ChoiceField(
        choices=autorespond_choices,
        widget=forms.RadioSelect,
        label=_('Autorespond requests'),
        help_text=_(
            'Should Mailman send an auto-response to emails sent to the '
            '-request address? If you choose yes, decide whether you want '
            'Mailman to discard the original email, or forward it on to the '
            'system as a normal mail command.'))
    autoresponse_request_text = forms.CharField(
        label=_('Autoresponse request text'),
        widget=forms.Textarea(),
        required=False,
        help_text=_('Auto-response text to send to -request emails.'))
    autoresponse_grace_period = forms.CharField(
        label=_('Autoresponse grace period'),
        help_text=_(
            'Number of days between auto-responses to either the mailing list '
            'or -request/-owner address from the same poster. Set to zero '
            '(or negative) for no grace period (i.e. auto-respond to every '
            'message).'))
    respond_to_post_requests = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Notify users of held messages'),
        help_text=_(
            'Should Mailman notify users about their messages held for '
            'approval. If you say \'No\', no notifications will be sent '
            'to users about the pending approval on their messages.'))
    send_welcome_message = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Send welcome message'),
        help_text=_(
            'Send welcome message to newly subscribed members? '
            'Turn this off only if you plan on subscribing people manually '
            'and don\'t want them to know that you did so. This option is '
            'most useful for transparently migrating lists from some other '
            'mailing list manager to Mailman.'))
    welcome_message_uri = forms.CharField(
        label=_('URI for the welcome message'),
        required=False,
        help_text=_(
            'If a welcome message is to be sent to subscribers, you can '
            'specify a URI that gives the text of this message.'),
    )
    goodbye_message_uri = forms.CharField(
        label=_('URI for the good bye message'),
        required=False,
        help_text=_(
            'If a good bye message is to be sent to unsubscribers, you can '
            'specify a URI that gives the text of this message.'),
    )
    admin_immed_notify = forms.BooleanField(
        widget=forms.RadioSelect(choices=((True, _('Yes')), (False, _('No')))),
        required=False,
        label=_('Admin immed notify'),
        help_text=_(
            'Should the list moderators get immediate notice of new requests, '
            'as well as daily notices about collected ones? List moderators '
            '(and list administrators) are sent daily reminders of requests '
            'pending approval, like subscriptions to a moderated list, '
            'or postings that are being held for one reason or another. '
            'Setting this option causes notices to be sent immediately on the '
            'arrival of new requests as well. '))
    admin_notify_mchanges = forms.BooleanField(
        widget=forms.RadioSelect(choices=((True, _('Yes')), (False, _('No')))),
        required=False,
        label=_('Notify admin of membership changes'),
        help_text=_('Should administrator get notices of '
                    'subscribes and unsubscribes?'))


class ListIdentityForm(ListSettingsForm):
    """
    List identity settings.
    """
    advertised = forms.TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        label=_('Show list on index page'),
        help_text=_('Choose whether to include this list '
                    'on the list of all lists'))
    description = forms.CharField(
        label=_('Description'),
        required=False,
        help_text=_(
            'This description is used when the mailing list is listed with '
            'other mailing lists, or in headers, and so forth. It should be '
            'as succinct as you can get it, while still identifying what the '
            'list is.'),
    )
    info = forms.CharField(
        label=_('Information'),
        help_text=_('A longer description of this mailing list.'),
        required=False,
        widget=forms.Textarea())
    display_name = forms.CharField(
        label=_('Display name'),
        required=False,
        help_text=_('Display name is the name shown in the web interface.')
    )
    subject_prefix = forms.CharField(
        label=_('Subject prefix'),
        strip=False,
        required=False,
    )

    def clean_subject_prefix(self):
        """
        Strip the leading whitespaces from the subject_prefix form field.
        """
        return self.cleaned_data.get('subject_prefix', '').lstrip()


class ListMassSubscription(forms.Form):
    """Form fields to masssubscribe users to a list.
    """
    emails = ListOfStringsField(
        label=_('Emails to mass subscribe'),
        help_text=_(
            'The following formats are accepted:\n'
            'jdoe@example.com\n'
            '&lt;jdoe@example.com&gt;\n'
            'John Doe &lt;jdoe@example.com&gt;\n'
            '"John Doe" &lt;jdoe@example.com&gt;\n'
            'jdoe@example.com (John Doe)\n'
            'Use the last three to associate a display name with'
            ' the address\n'),
    )


class ListMassRemoval(forms.Form):

    """Form fields to remove multiple list users.
    """
    emails = ListOfStringsField(
        label=_('Emails to Unsubscribe'),
        help_text=_('Add one email address on each line'),
    )

    class Meta:

        """
        Class to define the name of the fieldsets and what should be
        included in each.
        """
        layout = [["Mass Removal", "emails"]]


class ListAddBanForm(forms.Form):
    """Ban an email address for a list."""
    # TODO maxking: This form should only accept valid emails or regular
    # expressions. Anything else that doesn't look like a valid email address
    # or regexp for email should not be a valid value for the field. However,
    # checking for that might not be easy.
    email = forms.CharField(
        label=_('Add ban'),
        help_text=_(
            'You can ban a single email address or use a regular expression '
            'to match similar email addresses.'),
        error_messages={
            'required': _('Please enter an email address.'),
            'invalid': _('Please enter a valid email address.')})


class ListHeaderMatchForm(forms.Form):
    """Edit a list's header match."""

    HM_ACTION_CHOICES = [(None, _("Default antispam action"))] + \
                        [a for a in ACTION_CHOICES if a[0] != 'defer']

    header = forms.CharField(
        label=_('Header'),
        help_text=_('Email header to filter on (case-insensitive).'),
        error_messages={
            'required': _('Please enter a header.'),
            'invalid': _('Please enter a valid header.')})
    pattern = forms.CharField(
        label=_('Pattern'),
        help_text=_('Regular expression matching the header\'s value.'),
        error_messages={
            'required': _('Please enter a pattern.'),
            'invalid': _('Please enter a valid pattern.')})
    action = forms.ChoiceField(
        label=_('Action'),
        error_messages={'invalid': _('Please enter a valid action.')},
        required=False,
        choices=HM_ACTION_CHOICES,
        help_text=_('Action to take when a header matches')
    )


class ListHeaderMatchFormset(forms.BaseFormSet):
    def clean(self):
        """Checks that no two header matches have the same order."""
        if any(self.errors):
            # Don't bother validating the formset unless
            # each form is valid on its own
            return
        orders = []
        for form in self.forms:
            try:
                order = form.cleaned_data['ORDER']
            except KeyError:
                continue
            if order in orders:
                raise forms.ValidationError('Header matches must have'
                                            ' distinct orders.')
            orders.append(order)


class MemberModeration(forms.Form):
    """
    Form handling the member's moderation_action.
    """
    moderation_action = forms.ChoiceField(
        widget=forms.Select(),
        label=_('Moderation'),
        required=False,
        choices=[(None, _('List default'))] + list(ACTION_CHOICES),
        help_text=_(
            'Default action to take when this member posts to the list. \n'
            'List default -- follow the list\'s default member action. \n'
            'Hold -- This holds the message for approval by the list '
            'moderators. \n'
            'Reject -- this automatically rejects the message by sending a '
            'bounce notice to the post\'s author. The text of the bounce '
            'notice can be configured by you. \n'
            'Discard -- this simply discards the message, with no notice '
            'sent to the post\'s author. \n'
            'Accept -- accepts any postings without any further checks. \n'
            'Defer -- default processing, run additional checks and accept '
            'the message. \n'))


class ChangeSubscriptionForm(forms.Form):
    email = forms.ChoiceField()

    def __init__(self, user_emails, *args, **kwargs):
        super(ChangeSubscriptionForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.ChoiceField(
            label=_('Select Email'),
            required=False,
            widget=forms.Select(),
            choices=((address, address) for address in user_emails))
