// Service Worker for Academia Validator - Offline Functionality
const CACHE_NAME = 'academia-validator-v1.0';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/admin',
  '/test',
  '/api/institutions',
  '/offline.html'
];

// Install event - cache resources
self.addEventListener('install', event => {
  console.log('📦 Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('📦 Service Worker: Caching files');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('🚀 Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️ Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Handle different types of requests
  if (request.method === 'GET') {
    event.respondWith(
      caches.match(request)
        .then(response => {
          // Return cached version if available
          if (response) {
            console.log('📦 Service Worker: Serving from cache:', request.url);
            return response;
          }
          
          // Try to fetch from network
          return fetch(request)
            .then(response => {
              // Don't cache if not a valid response
              if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
              }
              
              // Clone the response
              const responseToCache = response.clone();
              
              // Add to cache
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(request, responseToCache);
                });
              
              return response;
            })
            .catch(() => {
              // Show offline page for navigation requests
              if (request.destination === 'document') {
                return caches.match('/offline.html');
              }
              
              // Return a basic response for other requests
              return new Response('Offline - Content not available', {
                status: 503,
                statusText: 'Service Unavailable'
              });
            });
        })
    );
  }
  
  // Handle POST requests (certificate verification)
  else if (request.method === 'POST' && url.pathname === '/api/verify') {
    event.respondWith(
      handleOfflineVerification(request)
    );
  }
});

// Handle offline certificate verification
async function handleOfflineVerification(request) {
  try {
    // Try to process online first
    const response = await fetch(request);
    return response;
  } catch (error) {
    // Handle offline verification
    console.log('🔌 Processing verification offline...');
    
    // Extract form data
    const formData = await request.formData();
    const file = formData.get('certificate');
    
    if (!file) {
      return new Response(JSON.stringify({
        success: false,
        error: 'No file provided'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Store verification request for later sync
    await storeOfflineVerification({
      file: file,
      timestamp: Date.now(),
      status: 'pending'
    });
    
    return new Response(JSON.stringify({
      success: true,
      offline: true,
      message: 'Verification queued for processing when online',
      filename: file.name,
      status: 'offline_queued'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Store offline verification requests
async function storeOfflineVerification(data) {
  const db = await openOfflineDB();
  const transaction = db.transaction(['offline_verifications'], 'readwrite');
  const store = transaction.objectStore('offline_verifications');
  await store.add(data);
}

// Open IndexedDB for offline storage
function openOfflineDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('AcademiaValidatorOffline', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = event => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('offline_verifications')) {
        const store = db.createObjectStore('offline_verifications', { keyPath: 'id', autoIncrement: true });
        store.createIndex('timestamp', 'timestamp', { unique: false });
        store.createIndex('status', 'status', { unique: false });
      }
    };
  });
}

// Background sync for offline verifications
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync-verifications') {
    event.waitUntil(syncOfflineVerifications());
  }
});

// Sync offline verifications when back online
async function syncOfflineVerifications() {
  console.log('🔄 Syncing offline verifications...');
  
  const db = await openOfflineDB();
  const transaction = db.transaction(['offline_verifications'], 'readonly');
  const store = transaction.objectStore('offline_verifications');
  const pendingRequests = await store.index('status').getAll('pending');
  
  for (const request of pendingRequests) {
    try {
      const formData = new FormData();
      formData.append('certificate', request.file);
      
      const response = await fetch('/api/verify', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        // Mark as synced
        const updateTransaction = db.transaction(['offline_verifications'], 'readwrite');
        const updateStore = updateTransaction.objectStore('offline_verifications');
        request.status = 'synced';
        await updateStore.put(request);
        
        console.log('✅ Synced verification:', request.id);
      }
    } catch (error) {
      console.log('❌ Failed to sync verification:', request.id, error);
    }
  }
}

// Listen for online/offline events
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CHECK_OFFLINE_STATUS') {
    event.ports[0].postMessage({
      isOnline: navigator.onLine,
      cacheSize: urlsToCache.length
    });
  }
});