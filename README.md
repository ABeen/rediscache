# rediscache

The Python interface to the redis-py.

## Getting Started

```Python

    from rediscache import LogicContext, get_context
    from rediscache import (set_cache, get_cache, del_cache, op_cache, set_hash_cache)

    def test_cache():
        with LogicContext():
            set_cache("name", "abeen")
            value = get_cache("name")
            print value
            
            del_cache("name")
            value = get_cache("name")
            print value

            name = "zhang sheng"
            student = {"name" : name, "age" : 21, "address" : "Beijing"}
            set_hash_cache(name, student)
            cache = get_context().get_cache(name)
            result = cache.hgetall(name)
            address = cache.hget(name, "address")
            print result, address
```
