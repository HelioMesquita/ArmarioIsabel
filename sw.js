self.ARMARIO_CACHE_NAME = "armario-isabel-static-a36a3b82d77d";
self.ARMARIO_APP_ASSETS = [
  "./",
  "./index.html",
  "./public/app.js",
  "./public/styles.css",
  "./app-config.json",
  "./manifest.webmanifest",
  "./public/icons/icon.svg",
  "./public/icons/icon-180.png",
  "./public/icons/icon-192.png",
  "./public/icons/icon-512.png"
];
self.ARMARIO_EXTRA_PRECACHE = [
  "./catalog.json"
];
const CACHE_NAME = self.ARMARIO_CACHE_NAME || "armario-isabel-v3";
const APP_ROOT = new URL("./", self.location.href).toString();
const DEFAULT_APP_ASSETS = [
  "./",
  "./index.html",
  "./app.js",
  "./styles.css",
  "./app-config.json",
  "./manifest.webmanifest",
  "./icons/icon.svg",
  "./icons/icon-180.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
];
const APP_ASSETS = [
  ...(self.ARMARIO_APP_ASSETS || DEFAULT_APP_ASSETS),
  ...(self.ARMARIO_EXTRA_PRECACHE || []),
];

function isCacheable(response) {
  return response && response.ok && response.type === "basic";
}

async function fetchAndCache(request) {
  const response = await fetch(request);
  if (isCacheable(response)) {
    const cache = await caches.open(CACHE_NAME);
    await cache.put(request, response.clone());
  }
  return response;
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) =>
        cache.addAll(
          APP_ASSETS.map(
            (asset) => new Request(new URL(asset, self.location.href), { cache: "reload" }),
          ),
        ),
      )
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))),
      )
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== self.location.origin) return;

  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/media/")) {
    event.respondWith(fetch(event.request));
    return;
  }

  event.respondWith(
    fetchAndCache(event.request).catch(() =>
      caches
        .match(event.request)
        .then((cached) =>
          cached || (event.request.mode === "navigate" ? caches.match(APP_ROOT) : undefined),
        ),
    ),
  );
});
