// This is the code piece that GenerateSW mode can't provide for us.
// This code listens for the user's confirmation to update the app.
import { Route, Router, RegExpRoute } from 'workbox-routing';
import NetworkFirst from 'workbox-strategies';
import Plugin from 'workbox-expiration';
import precacheAndRoute from 'workbox-precaching';
import clientsClaim from 'workbox-core'


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
      break;
    default:
      // NOOP
      break;
  }
});

clientsClaim();

const router = new Router();
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
  var networkFirstPaths = [
    'api/v1/',
    'media/',
  ]
  var networkFirstExcludedPaths = [
    'api/v1/listen'
  ]
  var strategy = new NetworkFirst({
    cacheName: "api-cache:" + serverUrl,
    plugins: [
      new Plugin({
        maxAgeSeconds: 24 * 60 * 60 * 7,
      }),
    ]
  })
  var networkFirstRoutes = networkFirstPaths.map((path) => {
    var regex = new RegExp(regexReadyServerUrl + path)
    return new RegExpRoute(regex, () => {})
  })
  var matcher = ({url, event}) => {
    for (let index = 0; index < networkFirstExcludedPaths.length; index++) {
      const blacklistedPath = networkFirstExcludedPaths[index];
      if (url.pathname.startsWith('/' + blacklistedPath)) {
        // the path is blacklisted, we don't cache it at all
        console.log('[sw] Path is blacklisted, not caching', url.pathname)
        return false
      }
    }
    // we call other regex matchers
    for (let index = 0; index < networkFirstRoutes.length; index++) {
      const route = networkFirstRoutes[index];
      let result = route.match({url, event})
      if (result) {
        return result
      }
    }
    return false
  }

  var route = new Route(matcher, strategy)
  console.log('[sw] registering new API route...', route)
  router.registerRoute(route)
  registeredServerRoutes.push(route)
}

// The precaching code provided by Workbox.
self.__precacheManifest = [].concat(self.__precacheManifest || []);

// workbox.precaching.suppressWarnings(); // Only used with Vue CLI 3 and Workbox v3.
precacheAndRoute(self.__precacheManifest, {});
