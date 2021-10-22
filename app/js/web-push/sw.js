'use strict';

self.addEventListener("push", function(event) {
    console.log('[Service Worker] Push Received.');
    console.log('[Service Worker] Push had this data: "${event.data.text()}"');
  
    if (event.data) {
        var data = event.data.json()
        showLocalNotification(data, self.registration);
    }
});

const showLocalNotification = (data, swRegistration) => {
    const options = {
        body: data.body,
		data: data,
        badge: data.badge,
        icon: data.icon,
    };
    swRegistration.showNotification(data.title, options);
};

self.addEventListener('notificationclick', function(event) {
    console.log('[Service Worker] Notification click Received.');
    event.notification.close();
    event.waitUntil(clients.openWindow(event.notification.data.url));
});

// Chrome unfortunately requires a fetch event handler to be in place for an app to be
// considered "installable", even if there is no reason to handle the event. We get around
// this by simply adding a trivial handler.
self.addEventListener('fetch', function() {});
