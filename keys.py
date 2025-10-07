import json

def make_cache_key(url, request) -> str:
    params_set = frozenset(request.query_params.items()) if request.query_params else None

    key_data = {
        "url": url,
        "params": sorted(params_set) if params_set else None,
    }
    return "cache:" + json.dumps(key_data, sort_keys=True)

def make_vary_key(request, response) -> str:
    vary = response.headers.get("Vary")
    vary_headers = [h.strip() for h in vary.split(",")] if vary else []
    return json.dumps([(h, request.headers.get(h)) for h in vary_headers])