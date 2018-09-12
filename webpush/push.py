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

from push_notifications.webpush import WebPushError


def send_web_push(web_push_record, device):
    '''
    Send a push notification to a subscribed device
    Save the status into the WebPushRecord model
    '''
    try:
        # send the request to the endpoint
        response = device.send_message(web_push_record.payload, ttl=web_push_record.ttl)
        web_push_record.response = json.dumps(response)
        if 'success' in response and response['success'] == 1:
            web_push_record.set_status_ok()
        else:
            web_push_record.set_status_err()
    except WebPushError as wperr:
        web_push_record.set_status_err()
        raise

    return web_push_record
