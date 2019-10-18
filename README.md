# django-webpush-demo

A demo django server using jazzband's django-push-notifications (https://github.com/jazzband/django-push-notifications), Django rest framework and web-push-libs modules standardizing Push API (https://github.com/web-push-libs).

It features a callback storing the user response when receiving the push notification. It's compatible with any browser supporting native push notifications with the Push API and Service workers (https://developer.mozilla.org/fr/docs/Web/API/Push_API)

 * webpush.js and service-worker.js for the client-side. Notifications are displayed with an default icon, two action buttons (OK, forget), and a click handler opening/focusing the browser on the URL carried by the notification data.
 * webpush/urls.py for the server's API
 * webpush/management/commands/send_webpush.py for server's cron-job to send the pending notifications

## How-to configure VAPID

 * After cloning this repository, please install the python environment

```bash
    cd django-webpush-demo
    virtualenv .venv --python=python3
    source .venv/bin/activate
    pip install -r requirements.txt
```

 * Create a temporary file (claim.json) to create your signing keys:

```javascript
   {
     "sub": "mailto: my@email.me",
     "aud": "https://fcm.googleapis.com"
   }
```

 * Generate client public key (applicationServerKey) and public and private keys

```bash
     vapid --applicationServerKey
```

[output]

```bash
       Application Server Key = BEFuGfKKEFp-kEB...JlkA34llWF0xHya70
```

## More...

The web Push API specification : https://developer.mozilla.org/fr/docs/Web/API/Push_API
A nice demonstration of VAPID is https://gauntface.github.io/simple-push-demo/
Another nico resource from google.com :https://developers.google.com/web/fundamentals/push-notifications/sending-messages-with-web-push-libraries

 * Django settings:

  * Create your own local_settings.py next to settings.py, and add Application Server Key to  `PUSH_NOTIFICATIONS_SETTINGS['APP_SERVER_KEY']`
  * Modify the key WP_CLAIMS in settings.py : "sub" with the same email used in the file claim.json. Do not add the "aud", because the push servers could be Mozilla's or Google's, and django-push-notifications takes care of that

## Install and run the Django server

```
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
```

## Push !

 * login with your admin account at http://localhost:8000/admin
 * check the subscribe box at http://localhost:8000, then check the user's subscription status at http://localhost:8000/admin/push_notifications/webpushdevice/
 * ![step 1: click the checkbox and allow push](step-2-allow-push-api.png)
 * ![step 2 : check the subscription state](step-2-subscription-status-admin.png)
 * create the push notifications content at http://localhost:8000/admin/webpush/notification
 * ![step " : create the notification contents](step-3-notification-model-admin.png)
 * then execute the command :

```bash
    python manage.py send_webpush
    
  Found a device id =  8 to push the notification id = 1
```

  * wait for the notification to show on your device !
 ![Result : how the result displays in Chromium (disable gnome native to see buttons and images)](step-4-chromium-show-push.png)
  * check the status of the notification at http://localhost:8000/admin/webpush/notification/ (`is read`) and http://localhost:8000/admin/webpush/webpushrecord/ (`is sent`)
  * native notifications also can be tested on your mobile device !
  * in the server, the method that sends the notification to the browser's vendor servers is here https://github.com/jazzband/django-push-notifications/blob/master/push_notifications/webpush.py

## TODO

  * UI obviously
  * Better documentation
  * Tests !
  * Replace the booleans `is read` and `is sent` (read previous section) Store a timestamp when sending the notification, store a timestamp when receiving the callback when the user clicks on an action button on the push notification (OK or Forget).
