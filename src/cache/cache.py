import json
import time
import httpx
import redis
from .directives import check_directive, check_cache_behaviour
from .keys import make_cache_key, make_vary_key

async def _revalidate_cache(url, request, cached_response):
    new_headers = dict(request.headers)
    new_headers["If-None-Match"] = cached_response["headers"].get("etag")
    if new_headers["If-None-Match"] == None:
        return None

    async with httpx.AsyncClient() as client:
        forwarded_response = await client.request(
            method=request.method,
            url=url,
            params=request.query_params,
            headers=new_headers
        )
    if forwarded_response.status_code == 304:
        return cached_response
    else:
        return None

async def get_from_cache(r, url: str, request):
    request_cache_behaviour = check_cache_behaviour(request.headers)
    if request_cache_behaviour in ("no-store", "no-cache", "private"):
        return None

    key = make_cache_key(url, request)
    raw = r.get(key)
    responses = {} if raw is None else json.loads(raw)

    for vary_headers_key_str in responses.keys():
        vary_headers_key = json.loads(vary_headers_key_str)
        if all(request.headers.get(h) == v for h, v in vary_headers_key):
            cached_response = responses[vary_headers_key_str] 
            response_cache_behaviour = check_cache_behaviour(cached_response["headers"])

            if "must-revalidate" in (request_cache_behaviour, response_cache_behaviour):
                return await _revalidate_cache(url, request, cached_response)

            expire_time = cached_response["expire_time"]
            if response_cache_behaviour == "immutable" or expire_time is None or expire_time > time.time():
                return cached_response
            else:
                max_stale = check_directive("max-stale", request.headers)
                #if max_stale is False then no such directive was found, if it's True then the directive with no value was found so it accepts any staleness
                if max_stale is False or max_stale is True or expire_time - time.time() + int(max_stale) > 0:
                    return cached_response
                return None
    return None

def add_to_cache(r, url: str, request, response):
    ttl = 3600
    max_age = check_directive("max-age", response.headers)
    if max_age:
        ttl = int(max_age)

    behaviour = check_cache_behaviour(response.headers)
    if behaviour in ("no-store", "no-cache", "private"):
        return

    key = make_cache_key(url, request)
    raw = r.get(key)
    data = {} if raw is None else json.loads(raw)

    value = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "content": response.text,
        "expire_time": time.time() + ttl
    }

    sub_key = make_vary_key(request, response)
    data[sub_key] = value
    r.set(key, json.dumps(data))

def clear_stale_cache(r):
    current_time = time.time()

    for key in r.scan_iter('*'):
        values = json.loads(r.get(key))
        if not values:
            continue

        fresh = { sub_key: value for sub_key, value in values.items() if value.get("expire_time", 0) > current_time }

        if fresh != values:
            if fresh:
                r.set(key, json.dumps(fresh))
            else:
                r.delete(key)
            print(f"Cleaned {key}: {len(values) - len(fresh)} stale entries removed.")