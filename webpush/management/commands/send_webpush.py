# -*- coding: utf-8 -*-
# by Elias Showk <elas@showk.me>
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from dateutil.parser import parse
from datetime import timedelta
import argparse

import django
from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware, now, is_naive

from webpush.models import Notification, WebPushRecord
from webpush.push import send_web_push

from push_notifications.models import WebPushDevice

def to_datetime_argument(string):
    try:
        return make_aware(parse(string))
    except ValueError as verr:
        raise argparse.ArgumentTypeError(verr)


class Command(BaseCommand):
    help = u'''Send push notification for the last notifications, for example :

        $ python manage.py send_webpush --since=2018-03-03T00:00:00

    this will send all waiting web push notifications from march 3rd 2018 until now
    '''

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--since',
            dest='since',
            default=None,
            type=to_datetime_argument,
            help='Send push notifications created since this datetime',
        )

    def handle(self, *args, **options):
        ''' Send visible and new web-push notifications
        '''
        if django.VERSION < (1, 11):
            print('Exiting send_webpush : running an incompatible version of Django (%s)' % (django.VERSION))
            return
        verbosity = options.get('verbosity', 1)
        since = options.get('since')
        if since is None:
            since = now() - timedelta(hours=24)

        if is_naive(since):
            since = make_aware(since)

        for notification in Notification.objects.new().visible().filter(valid_from__gte=since):
            for device in WebPushDevice.objects.filter(user=notification.user, active=True):
                with transaction.atomic():
                    web_push_record, created = WebPushRecord.objects.select_for_update().get_or_create(
                        notification=notification,
                        subscription=device)
                    if web_push_record.status == WebPushRecord.DEFAULT_STATUS:
                        if verbosity > 0:
                            print('Found a device id =  %s to push the notification id = %s' % (device.id, notification.id))

                        web_push_record = send_web_push(web_push_record, device)
