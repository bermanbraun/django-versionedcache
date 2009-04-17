import time

from django.core.cache.backends import memcached, base
from django.utils.encoding import smart_unicode, smart_str

from django.conf import settings

DEFAULT_TIMEOUT_RATIO = 3.0/4.0

class CacheClass(memcached.CacheClass):

    def _tag_key(self, key):
        return getattr(settings, 'VERSION', '') + smart_str(key)

    def _tag_value(self, value, timeout):
        """
        Add staleness information to the value when setting.

        return value tuple and timeout
        """
        t = timeout or self.default_timeout
        stale = t * getattr(settings, 'TIMEOUT_RATIO', DEFAULT_TIMEOUT_RATIO)
        stale_time = time.time() + stale
        delay = 2 * (t - stale)
        return (value, stale_time, delay), t

    def add(self, key, value, timeout=0):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return self._cache.add(self._tag_key(key), *self._tag_value(value, timeout))
 
    def get(self, key, default=None):
        key = self._tag_key(key)

        val = self._cache.get(key)

        if val:
            # unpack timeout
            val, stale_time, delay = val

            # cache is stale, refresh
            if stale_time and stale_time <= time.time():
                # keep the stale value in cache for delay seconds ...
                self._cache.set(key, (val, None, 0), delay)
                # ... and return the default so that the caller will regenerate the cache
                return default

        if val is None:
            return default
        else:
            if isinstance(val, basestring):
                return smart_unicode(val)
            else:
                return val 
 
    def set(self, key, value, timeout=0):
        if isinstance(value, unicode):
            value = smart_str(value)
        self._cache.set(self._tag_key(key), *self._tag_value(value, timeout))
 
    def get_many(self, keys):
        return map(lambda x: x[0], self._cache.get_multi(map(self._tag_key,keys)))
 
    def incr(self, key, delta=1):
        return base.BaseCache.incr(self, self._tag_key(key), delta)
 
    def decr(self, key, delta=1):
        return base.BaseCache.decr(self, self._tag_key(key), delta)
