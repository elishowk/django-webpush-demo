/* global self, caches, fetch, URL, Response */
'use strict';

var config = {
  version: 'v0.1',
  staticCacheItems: [],
  cachePathPattern: /^\/static\/.*/,
  handleFetchPathPattern: /.*/,
  offlinePage: '/'
};

function cacheName(key, opts) {
  return '${opts.version}-${key}';
}

function addToCache(cacheKey, request, response) {
  if (response.ok && cacheKey !== null) {
    var copy = response.clone();
    caches.open(cacheKey)
      .then(function (cache) {
        cache.put(request, copy);
      });
  }
  return response;
}

function fetchFromCache(event) {
  return caches.match(event.request)
    .then(response => {
      if (!response) {
        throw Error(`${event.request.url} not found in cache`);
      }
      return response;
    });
}

function offlineResponse(resourceType, opts) {
  if (resourceType === 'content') {
    return caches.match(opts.offlinePage);
  }
  return undefined;
}

self.addEventListener('install', event => {
  function onInstall(event, opts) {
    var cacheKey = cacheName('static', opts);
    return caches.open(cacheKey)
      .then(cache => cache.addAll(opts.staticCacheItems));
  }

  event.waitUntil(
    onInstall(event, config)
    .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  function onActivate(event, opts) {
    return caches.keys()
      .then(cacheKeys => {
        var oldCacheKeys = cacheKeys.filter(key => key.indexOf(opts.version) !== 0);
        var deletePromises = oldCacheKeys.map(oldKey => caches.delete(oldKey));
        return Promise.all(deletePromises);
      });
  }

  event.waitUntil(
    onActivate(event, config)
    .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {

  function shouldHandleFetch(event, opts) {
    var request = event.request;
    var url = new URL(request.url);
    var criteria = {
      matchesPathPattern: opts.handleFetchPathPattern.test(url.pathname),
      isGETRequest: request.method === 'GET',
      isFromMyOrigin: url.origin === self.location.origin
    };
    var failingCriteria = Object.keys(criteria)
      .filter(criteriaKey => !criteria[criteriaKey]);
    return !failingCriteria.length;
  }

  function onFetch(event, opts) {
    var request = event.request;
    var url = new URL(request.url);
    var acceptHeader = request.headers.get('Accept');
    var resourceType = 'static';
    var cacheKey;

    if (acceptHeader.indexOf('text/html') !== -1) {
      resourceType = 'content';
    } else if (acceptHeader.indexOf('image') !== -1) {
      resourceType = 'image';
    }

    cacheKey = null;
    if (opts.cachePathPattern.test(url.pathname)) {
      cacheKey = cacheName(resourceType, opts);
    }

    /* always network first */
    event.respondWith(
      fetch(request)
      .then(response => addToCache(cacheKey, request, response))
      .catch(() => fetchFromCache(event))
      .catch(() => offlineResponse(resourceType, opts))
    );
  }
  if (shouldHandleFetch(event, config)) {
    onFetch(event, config);
  }
});

/*
 * Return the options paramter for showNotification
 * Only Chrome has extended support for extra features like actions, badge, icon, etc
 * https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration/showNotification
 */
var getNotificationOptions = function (responseJson) {
  var options = {
    body: responseJson.body,
    icon: responseJson.icon,
    requireInteraction: 'true', // notification is persistent until a touch or click
    data: responseJson.data,
    actions: responseJson.actions
  };
  /* optional vibration */
  if (responseJson.vibrate) options.vibrate = responseJson.vibrate;
  return options;
};

/*
 * Push event handler
 * documentation at https://developers.google.com/web/fundamentals/push-notifications/display-a-notification
 */
self.addEventListener('push', function (event) {
  try {
    // Push is a JSON
    var responseJson = event.data.json();
    var title = responseJson.title;
    var options = getNotificationOptions(responseJson)
  } catch (err) {
    // Push is a simple text (usually debugging)
    var options = {
      'body': event.data.text()
    };
    var title = '';
  }
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function (event) {
  var urlToOpen = event.notification.data.open_url;
  switch (event.action) {
    case 'ack':
      break;
    case 'forget':
      break;
  }

  if (event.action) {
    // ack or forget
    fetch(event.notification.data.callback_url + '?action=' + event.action, {
        method: 'GET',
        mode: 'cors',
        cache: 'no-cache',
      })
      .catch(function () {
        console.log("error on GET ", event.notification.data.callback_url + '?action=' + event.action);
      });
  }
  // Check if there's already a tab open with this urlToOpen.
  event.waitUntil(self.clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then(function (windowClients) {
      let matchingClient = null;
      for (let i = 0; i < windowClients.length; i++) {
        const windowClient = windowClients[i];
        if (windowClient.url === urlToOpen) {
          matchingClient = windowClient;
          break;
        }
      }
      if (matchingClient) {
        return matchingClient.focus();
      } else {
        return clients.openWindow(urlToOpen);
      }
    })
  );
  // Android doesn't close the notification when you click it
  // See http://crbug.com/463146
  event.notification.close();
});
