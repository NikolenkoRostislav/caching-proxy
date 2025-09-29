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

def get_from_cache(cache: dict, url: str, params: dict):
    key = (url, frozenset(params.items()) if params else None)
    entry = cache.get(key)
    if entry:
        value, expire_time = entry
        if expire_time is None or expire_time > time.time():
            return value
        else:
            del cache[key]
    return None

def add_to_cache(cache: dict, url: str, params: dict, value, ttl: int = 60):
    key = (url, frozenset(params.items()) if params else None)
    expire_time = time.time() + ttl * 60
    cache[key] = (value, expire_time)