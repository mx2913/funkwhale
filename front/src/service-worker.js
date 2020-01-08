// This is the code piece that GenerateSW mode can't provide for us.
// This code listens for the user's confirmation to update the app.
workbox.loadModule('workbox-routing');
workbox.loadModule('workbox-strategies');
workbox.loadModule('workbox-expiration');

self.addEventListener('message', (e) => {
  if (!e.data) {
    return;
  }
  console.log('[sw] received message', e.data)
  switch (e.data.command) {
    case 'skipWaiting':
      self.skipWaiting();
      break;
    case 'serverChosen':
      self.registerServerRoutes(e.data.serverUrl)
    default:
      // NOOP
      break;
  }
});
workbox.core.clientsClaim();

// The precaching code provided by Workbox.
self.__precacheManifest = [].concat(self.__precacheManifest || []);
console.log('[sw] Files to be cached [before filtering]', self.__precacheManifest.length);
var excludedUrlsPrefix = [
  '/js/locale-',
  '/js/moment-locale-',
  '/js/admin',
  '/css/admin',
];
self.__precacheManifest = self.__precacheManifest.filter((e) => {
  return !excludedUrlsPrefix.some(prefix => e.url.startsWith(prefix))
});
console.log('[sw] Files to be cached [after filtering]', self.__precacheManifest.length);
// workbox.precaching.suppressWarnings(); // Only used with Vue CLI 3 and Workbox v3.
workbox.precaching.precacheAndRoute(self.__precacheManifest, {});

const router = new workbox.routing.Router();
router.addCacheListener()
router.addFetchListener()

var registeredServerRoutes = []
self.registerServerRoutes = (serverUrl) => {
  console.log('[sw] Setting up API caching for', serverUrl)
  registeredServerRoutes.forEach((r) => {
    console.log('[sw] Unregistering previous API route...', r)
    router.unregisterRoute(r)
  })
  if (!serverUrl) {
    return
  }
  var regexReadyServerUrl = serverUrl.replace('.', '\\.')
  registeredServerRoutes = []
  var networkFirstRoutes = [
    'api/v1/',
    'media/',
  ].map((path) => {
    return new RegExp(regexReadyServerUrl + path)
  })
  var strategy = new workbox.strategies.NetworkFirst({
    cacheName: "api-cache:" + serverUrl,
    plugins: [
      new workbox.expiration.Plugin({
        maxAgeSeconds: 24 * 60 * 60 * 7,
      }),
    ]
  })

  networkFirstRoutes.forEach((r) => {
    console.log('[sw] registering new API route...', r)
    var route = new workbox.routing.RegExpRoute(r, strategy)
    router.registerRoute(route)
    registeredServerRoutes.push(route)
  })
}
