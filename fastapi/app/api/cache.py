import hashlib
import logging
from time import time
from typing import Dict, List, Optional, Tuple
from collections import OrderedDict
from sys import getsizeof

CACHE_LIMIT = 10  # Max number of cached articles
TTL_SECONDS = 4000  # Time to live for cached items in seconds

"""
This module implements an LRU (Least Recently Used) cache for storing articles fetched from Wikipedia.
of the endpoint path. The above parameters are passed to the function as arguments which will determine
the time to live as well as the amount of elements which can be stored in the cache to prevent memory leaks.
This current implementation is exclusively insantiated and used in the wiki_article.py file, but can be 
extraported and used in other files in future implemenetations.
"""


# Internal LRU cache manager
class ArticleCache:
    # Initializes the cache
    def __init__(self, max_size: int = CACHE_LIMIT, ttl: int = TTL_SECONDS):
        self.cache: "OrderedDict[str, Dict]" = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.current_size = 0  # Approximate memory usage in bytes
    # Creates cache key
    def _get_cache_key(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, key: str) -> Tuple[Optional[str], Optional[List[str]]]:
        cache_key = self._get_cache_key(key)
        cached_data = self.cache.get(cache_key)
        # Checks cache for articles, misses if none are found
        if not cached_data:
            logging.info(f"[CACHE MISS] No cache entry for key: {cache_key}")
            return None, None
        # Cached article expires and is evicted if it exists longer than 4000 seconds (approx. 1.1 hours)
        if time() - cached_data["timestamp"] > self.ttl:
            self._evict(cache_key, reason="expired")
            return None, None

        self.cache.move_to_end(cache_key)
        logging.info(f"[CACHE HIT] Returning cached data for key: {cache_key}")
        return cached_data["content"], cached_data["languages"]
    # Sets cached article if it has not been cached yet
    def set(self, key: str, content: str, languages: List[str]) -> None:
        cache_key = self._get_cache_key(key)
        item = {
            "content": content,
            "languages": languages,
            "timestamp": time(),
        }
        # Determines size of article
        item_size = getsizeof(item)

        # Checks cache key and moves it accordingly based on LRU to enable effective eviction if needed
        if cache_key in self.cache:
            self.current_size -= getsizeof(self.cache[cache_key])
            self.cache.move_to_end(cache_key)
        elif len(self.cache) >= self.max_size:
            evicted_key, evicted_val = self.cache.popitem(last=False)
            self.current_size -= getsizeof(evicted_val)
            logging.info(f"[CACHE EVICTED] LRU item: {evicted_key}")

        self.cache[cache_key] = item
        self.current_size += item_size

        logging.info(f"[CACHE SET] Key: {cache_key} | Size: {len(self.cache)}/{self.max_size} | Approx. Memory: {self.current_size} bytes")
    # Nukes LRU article in the cache
    def _evict(self, key: str, reason: str = "manual") -> None:
        if key in self.cache:
            self.current_size -= getsizeof(self.cache[key])
            del self.cache[key]
            logging.info(f"[CACHE {reason.upper()}] Evicted key: {key}")

# Instantiate global cache object
_article_cache = ArticleCache()

# For external use
def get_article_cache_key(key: str) -> str:
    return _article_cache._get_cache_key(key)

def get_cached_article(title: str) -> Tuple[Optional[str], Optional[List[str]]]:
    return _article_cache.get(title)

def set_cached_article(key: str, content: str, languages: List[str]) -> None:
    _article_cache.set(key, content, languages)
