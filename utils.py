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

def _parse_cache_control_directives(headers: dict):
    cache_control = headers.get("cache-control") or ""
    return [d.strip() for d in cache_control.split(",")]

def check_directive(directive: str, headers: dict):
    directives = _parse_cache_control_directives(headers)
    if directive in directives:
        return True

    for d in directives:
        if d.startswith(directive):
            return d.split("=")[1]
    return False

def check_cache_behaviour(headers: dict):
    directives = _parse_cache_control_directives(headers)

    if "no-store" in directives:
        return "no-store"
    elif "no-cache" in directives:
        return "no-cache"
    elif "immutable" in directives:
        return "immutable"
    elif "must-revalidate" in directives:
        return "must-revalidate"
    else:
        return "default"

def get_from_cache(cache: dict, url: str, request):
    params_set = frozenset(request.query_params.items()) if request.query_params else None

    for cache_key in cache.keys():
        cache_url, cache_params, cache_vary_values = cache_key
        if cache_url != url or cache_params != params_set:
            continue

        if all(request.headers.get(h) == v for h, v in cache_vary_values):
            response, expire_time = cache[cache_key]
            behaviour = check_cache_behaviour(response.headers)
            if behaviour == "immutable" or expire_time is None or expire_time > time.time():
                return response
            else:
                del cache[cache_key]
                return None
    return None

def add_to_cache(cache: dict, url: str, request, response):
    ttl = 3600
    max_age = check_directive("max-age", response.headers)
    if max_age:
        ttl = int(max_age)

    behaviour = check_cache_behaviour(response.headers)
    if behaviour == "no-store" or behaviour == "no-cache":
        return

    vary = response.headers.get("Vary")
    vary_headers = [h.strip() for h in vary.split(",")] if vary else []
    vary_values = frozenset([(h, request.headers.get(h)) for h in vary_headers])
    params_set = frozenset(request.query_params.items()) if request.query_params else None

    key = (url, params_set, vary_values)
    expire_time = time.time() + ttl
    cache[key] = (response, expire_time)