import time
import argparse

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port number the proxy should listen on"
    )
    parser.add_argument(
        "--origin", "-o",
        required=True,
        help="Origin server URL to forward requests to"
    )

    return parser.parse_args()

def get_from_cache(cache: dict, url: str, params: dict, request_headers: dict):
    params_set = frozenset(params.items()) if params else None

    for cache_key in cache.keys():
        cache_url, cache_params, cache_vary_values = cache_key
        if cache_url != url or cache_params != params_set:
            continue

        if all(request_headers.get(h) == v for h, v in cache_vary_values):
            value, expire_time = cache[cache_key]
            if expire_time is None or expire_time > time.time():
                return value
            else:
                del cache[cache_key]
                return None
    return None


def add_to_cache(cache: dict, url: str, params: dict, request_headers: dict, value, response_headers: dict, ttl: int = 3600):
    vary = response_headers.get("Vary")
    vary_headers = [h.strip() for h in vary.split(",")] if vary else []
    vary_values = frozenset([(h, request_headers.get(h)) for h in vary_headers])
    params_set = frozenset(params.items()) if params else None

    key = (url, params_set, vary_values)
    expire_time = time.time() + ttl
    cache[key] = (value, expire_time)