import hashlib

from django.core.cache import cache


CACHE_TIMEOUT = 300
CACHE_VERSION_KEY = 'syllabuses:version'


def get_cache_version():
    version = cache.get(CACHE_VERSION_KEY)
    if version is None:
        cache.add(CACHE_VERSION_KEY, 1, timeout=None)
        version = cache.get(CACHE_VERSION_KEY, 1)
    return version


def syllabus_cache_key(user_id, scope, value=''):
    digest = hashlib.sha256(str(value).encode('utf-8')).hexdigest()[:16]
    return f'syllabuses:v{get_cache_version()}:u{user_id}:{scope}:{digest}'


def invalidate_syllabus_cache():
    try:
        cache.incr(CACHE_VERSION_KEY)
    except ValueError:
        cache.set(CACHE_VERSION_KEY, 2, timeout=None)
