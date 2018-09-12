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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json

from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from push_notifications.models import WebPushDevice
from push_notifications.api.rest_framework import WebPushDeviceAuthorizedViewSet

from webpush.models import Notification


def index(request):
    user = getattr(request, 'user', None)
    context = {}
    if user and user.is_authenticated:
        url = reverse('create-webpush-subscription')
        user_active_devices = [{
            'browser': device.browser,
            'registration_id': device.registration_id,
        } for device in WebPushDevice.objects.filter(user=user, active=True)]
        context.update({
            'url': url,
            'application_server_key': settings.PUSH_NOTIFICATIONS_SETTINGS['APP_SERVER_KEY'],
            'user_active_devices': json.dumps(user_active_devices),
        })

    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))


class NoCsrfAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check


class WebPushDeviceAuthorizedViewSetNoCsrf(WebPushDeviceAuthorizedViewSet):
    authentication_classes = (NoCsrfAuthentication,)


class NotificationCallback(GenericAPIView):
    '''
    Ack or forget a Notification object
    Anonymously but with a check on the user's public webpush registration key
    '''
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (NoCsrfAuthentication,)

    def get(self, request, notification_id, user, key, *args, **kwargs):
        action = request.GET['action']
        try:
            WebPushDevice.objects.get(p256dh=key)
            qs = Notification.objects.filter(user=user, id=notification_id)
            if action == 'ack':
                qs.read()
            if action == 'forget':
                qs.forget()
            return Response({'err': 0})
        except WebPushDevice.DoesNotExist:
            return Response({'err': 1}, status.HTTP_400_BAD_REQUEST)


notification_callback = NotificationCallback.as_view()
