const CACHE_PREFIX = 'ibo-learning-';
const CACHE_NAME = `${CACHE_PREFIX}v1`;
const MEDIA_PATTERN = /\.(?:mp4|m4v|mov|webm|mp3|m4a|wav|aac|ogg)(?:$|[?#])/i;
const STATIC_PATTERN = /\.(?:webp|jpg|jpeg|png|svg|vtt|json|css|js)(?:$|[?#])/i;
const fullAssetJobs = new Map();

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await Promise.allSettled(['./', './index.html'].map(url => cache.add(url)));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names
      .filter(name => name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME)
      .map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

async function safeCachePut(cache, key, response) {
  try {
    await cache.put(key, response);
  } catch (error) {
    // 存储空间不足或浏览器拒绝缓存时，不影响当前联网播放。
    console.warn('[offline-cache] cache put failed:', error);
  }
}

async function runFullAssetCache(url) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(url);
  if (cached && cached.status === 200) return cached;
  try {
    // 不携带视频播放器的 Range 头，保存一份可供下次离线读取的完整文件。
    const response = await fetch(new Request(url, { cache: 'default', credentials: 'same-origin' }));
    if (response.ok && response.status === 200) await safeCachePut(cache, url, response.clone());
    return response;
  } catch (_) {
    return cached || null;
  }
}

function cacheFullAsset(url) {
  if (fullAssetJobs.has(url)) return fullAssetJobs.get(url);
  const job = runFullAssetCache(url).finally(() => fullAssetJobs.delete(url));
  fullAssetJobs.set(url, job);
  return job;
}

async function serveRangeRequest(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request.url);
  if (!cached || cached.status !== 200) return fetch(request);

  const range = request.headers.get('range') || '';
  const match = /^bytes=(\d+)-(\d*)$/i.exec(range);
  if (!match) return cached;

  const body = await cached.arrayBuffer();
  const size = body.byteLength;
  const start = Number(match[1]);
  const requestedEnd = match[2] ? Number(match[2]) : size - 1;
  const end = Math.min(requestedEnd, size - 1);
  if (start >= size || start > end) {
    return new Response(null, {
      status: 416,
      headers: { 'Content-Range': `bytes */${size}` }
    });
  }

  const headers = new Headers(cached.headers);
  headers.set('Accept-Ranges', 'bytes');
  headers.set('Content-Range', `bytes ${start}-${end}/${size}`);
  headers.set('Content-Length', String(end - start + 1));
  return new Response(body.slice(start, end + 1), {
    status: 206,
    statusText: 'Partial Content',
    headers
  });
}

async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok && response.status === 200) await safeCachePut(cache, request, response.clone());
  return response;
}

async function staleWhileRevalidate(request, event) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  const update = fetch(request).then(async response => {
    if (response.ok && response.status === 200) await safeCachePut(cache, request, response.clone());
    return response;
  });
  if (cached) {
    event.waitUntil(update.catch(() => undefined));
    return cached;
  }
  return update;
}

async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  try {
    const response = await fetch(request);
    if (response.ok && response.status === 200) await safeCachePut(cache, request, response.clone());
    return response;
  } catch (_) {
    const cached = await cache.match(request);
    if (cached) return cached;
    throw _;
  }
}

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;

  if (MEDIA_PATTERN.test(url.pathname)) {
    if (request.headers.has('range')) {
      event.respondWith(serveRangeRequest(request));
      event.waitUntil(cacheFullAsset(request.url));
    } else {
      event.respondWith(cacheFirst(request));
    }
    return;
  }

  if (request.mode === 'navigate' || url.pathname.endsWith('/index.html') || url.pathname.endsWith('/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  if (STATIC_PATTERN.test(url.pathname)) {
    event.respondWith(staleWhileRevalidate(request, event));
  }
});
