#
# Copyright 2008, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

import logging
logger = logging.getLogger('bda.cache.cachemanager')

import time
from zope.interface import implements
from zope.component import adapts

from interfaces import ICacheManager
from interfaces import ICacheProvider

class CacheManager(object):
    """This class is responsible for manage cached objects.
    
    A ICacheProvider implementing object is adapted, and used as the current
    cache.
    """
    implements(ICacheManager)
    adapts(ICacheProvider)
    
    def __init__(self, context):
        """Take the cache object and a timeout in seconds as argument
        """
        self.timeout = 300 # defaults to 300 seconds
        self.cache = context
    
    def setTimeout(self, timeout):
        """Set the timeout for this cache.
        """
        self.timeout = timeout
    
    def getData(self, func, key, force_reload=False, args=[], kwargs={}):
        """Return cached data or call func, cache return value and return it.
        """
        from_cache = True
        
        ret = self.get(key, force_reload)
        
        if ret is None:
            from_cache = False
            ret = func(*args, **kwargs)
            self.set(key, ret)
        
        return ret
    
    def get(self, key, force_reload=False):
        """Return item with key or None.
        
        If force_reload is True, try to delete object with key from cache and
        return None.
        """
        if force_reload or self._isTimedOut(key):
            del self.cache[key]
            creationmap = self.cache.get('creationmap', None)
            
            if creationmap is not None and creationmap.has_key(key):
                del creationmap[key]
                self.cache['creationmap'] = creationmap
            
            return None
        
        return self.cache.get(key, None)
    
    def set(self, key, item, set_creationtime=True):
        """Store an item with key to cache. Optional you can manually specify
        if creation time should be set or not.
        """
        self.cache[key] = item
        
        if not set_creationtime:
            return
        
        creationmap = self.cache.get('creationmap', None)
        
        if not creationmap:
            creationmap = dict()
        
        creationmap[key] = time.time()
        self.cache['creationmap'] = creationmap
    
    def rem(self, key):
        """Remove item with key from cache if exists.
        """
        del self.cache[key]
        creationmap = self.cache.get('creationmap', None)
        
        if creationmap is not None and creationmap.has_key(key):
            del creationmap[key]
            self.cache['creationmap'] = creationmap
    
    def _isTimedOut(self, key):
        """Return wether the item with key is timed out or not.
        """
        cur = time.time()
        creationmap = self.cache.get('creationmap', None)
        
        if not creationmap:
            return True
        
        creationtime = creationmap.get(key, None)
        if not creationtime or creationtime + self.timeout < cur:
            return True
        
        return False 
