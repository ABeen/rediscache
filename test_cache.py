# -*- coding:utf-8 -*-
#
#   Author  :   ABeen
#   E-mail  :   abeen_8298@msn.com
#

from rediscache import LogicContext, get_context
from rediscache import (set_cache, get_cache, del_cache, op_cache,
        set_hash_cache, set_list_cache, set_set_cache, set_sorted_set_cache)

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





if __name__ == "__main__":
    test_cache()
