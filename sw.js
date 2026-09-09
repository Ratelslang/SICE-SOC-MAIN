const CACHE_NAME = 'sice-soc-main-v3-runtime-safe';
const APP_SHELL = [
  './',
  './SICE_SOC_MAIN_REDESIGNED.html',
  './OPS_.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(APP_SHELL).catch(() => undefined))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const requestUrl = new URL(event.request.url);
  // Browser extensions and other non-http schemes cannot be stored in CacheStorage.
  if (requestUrl.protocol !== 'http:' && requestUrl.protocol !== 'https:') return;
  event.respondWith(
    fetch(event.request)
      .then(response => {
        if (response && response.ok && requestUrl.origin === self.location.origin) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy)).catch(() => undefined);
        }
        return response;
      })
      .catch(() => caches.match(event.request).then(cached => {
        if (cached) return cached;
        if (event.request.mode === 'navigate') return caches.match('./SICE_SOC_MAIN_REDESIGNED.html');
        return Response.error();
      }))
  );
});
