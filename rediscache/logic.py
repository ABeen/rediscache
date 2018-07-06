# -*- coding:utf-8 -*-

"""
    逻辑模块

    LogicContext 封装了逻辑代码执行所需的上下文环境和对象。
    应该使用 with sgement 执行 LogicContext，确保资源被释放。
"""
from bisect import bisect_right
from hashlib import md5
from threading import local

from redis import Redis

CACHE_SERVERS = ("localhost", "localhost:6379")
SOCK_TIMEOUT = 3000


class ConsistentHash(object):
    """
        一致性哈希算法
    """

    _caches = {}

    def __init__(self, hosts, replicas = 10):
        self._hosts = {}
        self._ring = []
        self._build(hosts, replicas)


    def _build(self, hosts, replicas):
        for host in hosts:
            for i in xrange(replicas):
                key = "{0}_{1}".format(host, i)
                hsh = self._hash(key)

                self._hosts[str(hsh)] = host
                self._ring.insert(bisect_right(self._ring, hsh), hsh)            


    def _hash(self, s):
        return hash(md5(s).digest()) % 10000


    def get_host(self, key):
        hsh = self._hash(str(key))
        index = bisect_right(self._ring, hsh)
        if index >= len(self._ring): index = 0

        return self._hosts[str(self._ring[index])]


    @classmethod
    def get(cls, hosts):
        """
            从缓存中重复使用哈希环
        """
        key = str(hosts)
        if key not in cls._caches: cls._caches[key] = cls(hosts)
        return cls._caches[key]



class LogicContext(object):
    """
        逻辑上下文

        共享服务器连接。
        
        (1) 支持多个 Redis Cache Server，如: ("localhost", "127.0.0.1:9000")。
        (2) 可以在 settings.py 中修改默认设置。
    """

    # 多线程独立存储
    _thread_local = local()

    def __init__(self, cache_hosts = None, db_host = None):
        self._cache_hashs = ConsistentHash.get(cache_hosts or CACHE_SERVERS)
        self._caches = {}


    def __enter__(self):
        if not hasattr(self._thread_local, "contexts"): self._thread_local.contexts = []
        self._thread_local.contexts.append(self)
        return self


    def __exit__(self, exc_type, exc_value, trackback):
        self._thread_local.contexts.remove(self)
        self.close()


    def open(self):
        pass


    def close(self):
        for cache in self._caches.itervalues():
            cache.connection_pool.disconnect()


    def get_cache(self, name):
        host = self._cache_hashs.get_host(name)
        if host in self._caches: return self._caches[host]

        h, p = host.split(":") if ":" in host else (host, 6379)
        cache = Redis(host = h, port = int(p), socket_timeout = SOCK_TIMEOUT)
        self._caches[host] = cache

        return cache


    def get_mq(self, name):
        return self.get_cache(name)


    def get_collection(self, name, db_name = None):
        return self.get_db(db_name)[name]


    @classmethod
    def get_context(cls):
        """
            获取当前线程上下文对象，支持嵌套。
        """
        return hasattr(cls._thread_local, "contexts") and cls._thread_local.contexts and \
            cls._thread_local.contexts[-1] or None



get_context = LogicContext.get_context



__all__ = ["LogicContext", "get_context"] 
