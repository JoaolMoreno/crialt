import threading
import time
import hashlib
import json

class SimpleCache:
    def __init__(self, default_ttl=60):
        self.store = {}
        self.lock = threading.Lock()
        self.default_ttl = default_ttl

    def _make_key(self, prefix, params):
        key_str = json.dumps(params, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def get(self, prefix, params):
        key = self._make_key(prefix, params)
        with self.lock:
            entry = self.store.get(key)
            if entry:
                value, expires = entry
                if expires > time.time():
                    return value
                else:
                    del self.store[key]
        return None

    def set(self, prefix, params, value, ttl=None):
        key = self._make_key(prefix, params)
        expires = time.time() + (ttl or self.default_ttl)
        with self.lock:
            self.store[key] = (value, expires)

    def invalidate(self, prefix):
        with self.lock:
            keys_to_delete = [key for key in self.store if key.startswith(f"{prefix}:")]
            for key in keys_to_delete:
                del self.store[key]

cache = SimpleCache(default_ttl=60)
