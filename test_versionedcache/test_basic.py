# -*- coding: utf-8 -*-
import time

from django.core.cache import get_cache

from helpers import CachetestCase

from nose import tools

class TestMintCache(CachetestCase):
    def test_cache_expires(self):
        self.cache.set('cache-key', 'cache value', timeout=0.1)
        time.sleep(0.1)
        tools.assert_equals(None, self.cache.get('cache-key'))

    def test_cache_stales_only_once_after_some_time(self):
        self.cache.set('cache-key', 'cache value', timeout=.4)
        time.sleep(.35)
        tools.assert_equals(None, self.cache.get('cache-key'))
        tools.assert_equals('cache value', self.cache.get('cache-key'))

class TestVersioning(CachetestCase):
    def test_version_separation(self):
        c = get_cache('test_versionedcache.backend://?version=OLD')
        c.set('cache-key', 'cache value')
        c = get_cache('test_versionedcache.backend://?version=NEW')
        tools.assert_equals(None, c.get('cache-key'))

class TestMethods(CachetestCase):
    def test_incr_works(self):
        self.cache.set('key', 0)
        self.cache.incr('key')
        tools.assert_equals(1, self.cache.get('key'))

    def test_decr_works(self):
        self.cache.set('key', 10)
        self.cache.decr('key')
        tools.assert_equals(9, self.cache.get('key'))

    def test_incr_throws_error_on_non_existing_key(self):
        tools.assert_raises(ValueError, self.cache.incr, 'non-existent-key')

    def test_add_doesnt_set_cache_if_present(self):
        self.cache.set('cache-key', 'original cache value')
        x = self.cache.add('cache-key', 'cache value')
        tools.assert_equals(False, x)
        tools.assert_equals('original cache value', self.cache.get('cache-key'))

    def test_add_sets_cache_if_none_present(self):
        x = self.cache.add('cache-key', 'cache value')
        tools.assert_equals(True, x)
        tools.assert_equals('cache value', self.cache.get('cache-key'))

    def test_get_returns_default_on_empty_cache(self):
        tools.assert_equals('DEFAULT', self.cache.get('non-existent-key', 'DEFAULT'))

    def test_get_returns_None_on_empty_cache(self):
        tools.assert_equals(None, self.cache.get('non-existent-key'))

    def test_set_sets_cache(self):
        self.cache.set('cache-key', 'cache value')
        tools.assert_equals('cache value', self.cache.get('cache-key'))

    def test_add_works_with_unicode(self):
        un = u"你好 category"
        self.cache.add('cache-key', un)
        tools.assert_equals(un, self.cache.get('cache-key'))

    def test_set_works_with_unicode(self):
        un = u"你好 category"
        self.cache.set('cache-key', un)
        tools.assert_equals(un, self.cache.get('cache-key'))

    def test_set_many(self):
        self.cache.set_many({'k': 'value', 'k2': 'other-val'})
        tools.assert_equals('value', self.cache.get('k'))
        tools.assert_equals('other-val', self.cache.get('k2'))

    def test_get_many(self):
        self.cache.set('cache-key', 'cache value')
        self.cache.set('cache-key-herded', 'cache value II', 0.4)
        time.sleep(0.35)
        tools.assert_equals(
            {'cache-key': 'cache value'},
            self.cache.get_many(['cache-key', 'cache-key-herded', 'non-existent-key'])
        )
        tools.assert_equals(
            {'cache-key': 'cache value', 'cache-key-herded': 'cache value II'},
            self.cache.get_many(['cache-key', 'cache-key-herded', 'non-existent-key'])
        )

    def test_delete_deletes_versioned_cache(self):
        self.cache.set('key', 10)
        self.cache.delete('key')
        tools.assert_equals(None, self.cache.get('key'))

    def test_cache_key_is_not_versioned_twice(self):
        c = get_cache('test_versionedcache.backend://')
        c.set_many({'a': 42, 'b': 'value'})
        tools.assert_equals({'a': 42, 'b': 'value'}, c.get_many(['a', 'b']))
