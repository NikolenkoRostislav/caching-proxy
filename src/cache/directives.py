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
    options = ["private", "no-store", "no-cache", "immutable", "must-revalidate"]

    for directive in options:
        if directive in directives:
            return directive
    return "default"