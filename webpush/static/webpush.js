/* globals window, navigator, Uint8Array, $, Notification */
"use strict";
// Webpush Application controller
// by Elias Showk <elias@showk.me>
//
// This program is free software: you can redistribute it and/or modify it
// under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

// Utils functions:
function loadVersionBrowser(userAgent) {
  var ua = userAgent,
    tem, M = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
  if (/trident/i.test(M[1])) {
    tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
    return {
      name: 'IE',
      version: (tem[1] || '')
    };
  }
  if (M[1] === 'Chrome') {
    tem = ua.match(/\bOPR\/(\d+)/);
    if (tem != null) {
      return {
        name: 'Opera',
        version: tem[1]
      };
    }
  }
  M = M[2] ? [M[1], M[2]] : [navigator.appName, navigator.appVersion, '-?'];
  if ((tem = ua.match(/version\/(\d+)/i)) != null) {
    M.splice(1, 1, tem[1]);
  }
  return {
    name: M[0],
    version: M[1]
  };
}

function urlBase64ToUint8Array(base64String) {
  var padding = '='.repeat((4 - base64String.length % 4) % 4)
  var base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/')

  var rawData = window.atob(base64)
  var outputArray = new Uint8Array(rawData.length)

  for (var i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray;
}

$(function () {
    var subscribeButton,
      messageElt,
      sw;

    var activateTextMessage = 'Subscribe to notifications';
    var stopTextMessage = 'Stop notifications';
    var incompatibleMessage = 'This browser does not support push notifications.';

    subscribeButton = $('#webpush-subscribe-checkbox');
    messageElt = $('#webpush-subscribe-message');

    function uncheckSubscribeButton() {
      subscribeButton.attr('disabled', false);
      subscribeButton.attr('checked', false);
      subscribeButton.removeClass("checked");
      messageElt.text(activateTextMessage);
    }

    function checkSubscribeButton() {
      subscribeButton.attr('disabled', false);
      subscribeButton.attr('checked', true);
      subscribeButton.addClass("checked");
      messageElt.text(stopTextMessage);
    }
    // disable if not supported
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      messageElt.text(incompatibleMessage);
      subscribeButton.attr('checked', false);
      subscribeButton.attr('disabled', true);
      return;
    }
    // Get the initial subscription and refresh state from server
    if ('serviceWorker' in navigator) {
      var serviceWorkerSrc = '/static/service-worker.js';
      navigator.serviceWorker.register(serviceWorkerSrc)
        .then(function (reg) {
          sw = reg;
          // Get the initial Subscription
          sw.pushManager.getSubscription()
            .then(function (subscription) {
              // Check we have a subscription to unsubscribe
              if (!subscription) {
                // No subscription object, so we uncheck
                uncheckSubscribeButton();
              } else {
                // existing subscription object, so we check
                checkSubscribeButton();
              }
              refreshSubscription(reg);
            });
        });
    }


    subscribeButton.click(
      function () {
        messageElt.text('Please wait while connecting to the server...');
        subscribeButton.attr('disabled', true);
        refreshSubscription(sw);
      }
    );


    // Once the service worker is registered set the initial state
    function refreshSubscription(reg) {
      // If its denied, it's a permanent block until the
      if (Notification.permission === 'denied') {
        // Show a message and uncheck the button
        uncheckSubscribeButton();
        return;
      }
      // based on ":checked" being set before by pushManager.getSubscription()
      if (subscribeButton.filter(':checked').length > 0) {
        return subscribe(reg);
      } else {
        return unsubscribe(reg);
      }
    }


    // get the Subscription or register one new to POST to our server
    function subscribe(reg) {
      getOrCreateSubscription(reg)
        .then(function (subscription) {
          postSubscribeObj(true, subscription);
        })
        .catch(function (error) {
          messageElt.text('No connection, please retry later (debug = ' + error + ')');
        });
    }

    function getOrCreateSubscription(reg) {
      return reg.pushManager.getSubscription()
        .then(function (subscription) {
          var applicationServerKey, options;
          // Check if a subscription is available
          if (subscription) {
            return subscription;
          }
          applicationServerKey = subscribeButton.data('applicationServerKey');
          options = {
            userVisibleOnly: true, // required by chrome
            applicationServerKey: urlBase64ToUint8Array(applicationServerKey)
          };
          // If not, register one
          return reg.pushManager.subscribe(options)
        })
    }

    function unsubscribe() {
      // Get the Subscription to unregister
      sw.pushManager.getSubscription()
        .then(function (subscription) {
            // Check we have a subscription to unsubscribe
            if (!subscription) {
              // No subscription object, so set the state
              // to allow the user to subscribe to push
              uncheckSubscribeButton();
              return;
            }
            postSubscribeObj(false, subscription);
          })
    }

    /*
    * Send the parameter to the server
    * the type of the request, the name of the user subscribing,
    * and the push subscription endpoint + key the server needs
    * Each subscription is different on different browsers
    */
    function postSubscribeObj(active, subscription) {
      subscription = subscription.toJSON()
      var browser = loadVersionBrowser(navigator.userAgent);
      var endpointParts = subscription.endpoint.split('/');
      var registrationId = endpointParts[endpointParts.length - 1];
      var data = {
        'browser': browser.name.toUpperCase(),
        'p256dh': subscription.keys.p256dh,
        'auth': subscription.keys.auth,
        'name': 'notification-subscription',
        'registration_id': registrationId,
        'active': active
      };
      $.ajax({
        url: subscribeButton.data('apiUrl'),
        method: 'POST',
        data: JSON.stringify(data),
        dataType: 'json',
        crossDomain: true,
        cache: false,
        contentType: 'application/json; charset=UTF-8',
        xhrFields: { withCredentials: true }
      })
      .done(function (response) {
          // Check if the parameter is saved on the server
          if (response.active) {
            // Show the unsubscribe button
            checkSubscribeButton();
          }
          // Check if the information is deleted from server
          else if (!response.active) {
            // Get the Subscription
            getOrCreateSubscription(sw)
              .then(function (subscription) {
                  // Remove the subscription
                  subscription
                    .unsubscribe()
                    .then(function () {
                      // Show the subscribe button
                      uncheckSubscribeButton();
                    });
              })
              .catch(function () {
                subscribeButton.attr('disabled', false);
                subscribeButton.attr('checked', false);
                subscribeButton.removeClass("checked");
                messageElt.text('Subscription error, please retry later');
              });
          }
        })
        .fail(function () {
          messageElt.text('Subscription error, please retry later');
        });
    }
  }
);
