# -*- coding: utf-8 -*-
# by Elias Showk <elias@showk.me>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with

import json

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.timezone import now, timedelta

from push_notifications.models import WebPushDevice


class NotificationQuerySet(QuerySet):

    def visible(self, user=None, n=None):
        qs = self
        if user:
            qs = qs.filter(user=user)
        n = n or now()
        qs = qs.filter(Q(valid_from__lte=n) & (Q(valid_until__isnull=True) | Q(valid_until__gte=n)))
        return qs.order_by('-valid_from')

    def new(self):
        return self.filter(read=False)

    def read(self):
        self.update(read=True)

    def forget(self):
        past_end = now() - timedelta(seconds=5)
        self.update(valid_until=past_end, read=True)


class Notification(models.Model):
    """
    Notification content
    """
    objects = NotificationQuerySet.as_manager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=140)
    body = models.TextField(_('Body'), default='', blank=True)
    url = models.URLField(_('URL to open after a click/touch'), default='', blank=True)
    valid_from = models.DateTimeField(_('Validity start date and time'))
    valid_until = models.DateTimeField(_('Validity end date and time'), null=True)
    read = models.BooleanField(_('is Read'), default=False)

    class Meta:
        verbose_name = _('Notification')

    def __str__(self):
        return self.title


class WebPushRecord(models.Model):
    '''
    Store the state of a user's push notification
    '''
    DEFAULT_STATUS = 'NEW'
    ERR_STATUS = 'ERR'
    OK_STATUS = 'SENT'
    STATUS = (
        (DEFAULT_STATUS, 'Not-sent notification'),
        (OK_STATUS, 'Sent notification'),
        (ERR_STATUS, 'Invalid notification'),
    )
    subscription = models.ForeignKey(WebPushDevice, null=False, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, null=False, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(blank=True, auto_now_add=True)
    status = models.CharField(blank=True, max_length=4, choices=STATUS, default=DEFAULT_STATUS)
    response = models.TextField(null=True)

    class Meta:
        unique_together = ('subscription', 'notification')

    @property
    def ttl(self):
        delta = self.notification.valid_until - self.notification.valid_from
        return int(delta.total_seconds())

    @property
    def payload(self):
        '''
        JSON string sent to the push service.
        Every options are not supported by all browsers, adoption is progressive
        '''
        payload = {
            'title': self.notification.title,
            'body': "%s\n - %s" % (self.notification.body, self.notification.url),
            'icon': '/'.join((settings.STATIC_URL, 'notification-icon-460px.png')),
            'actions': [
                {'action': 'ack', 'title': _('OK'), 'icon': ''},
                {'action': 'forget', 'title': _('Forget'), 'icon': ''}
            ],
            # arbitraty data used by the service worker
            'data': {
                'callback_url': reverse('webpush-notification-callback', args=[self.notification.id, self.notification.user.id,
                          self.subscription.p256dh]),
                'open_url': self.notification.url
            },
            'vibrate': [200, 100, 400],
        }
        return json.dumps(payload)

    def set_status_ok(self):
        self.status = self.OK_STATUS
        self.save()

    def set_status_err(self):
        self.status = self.ERR_STATUS
        self.save()
