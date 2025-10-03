import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from utils import *

def create_app(origin: str, port: int):
    app = FastAPI()
    cache = {}

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def proxy(path: str, request: Request):
        url = f"{origin}/{path}"
        print(origin)
        print(port)
        print(url)
        
        if request.method == "GET":
            response = get_from_cache(cache, url, request.query_params, request.headers)

            if response:
                print("returned from cache")
                return Response(
                    content = response.content,
                    status_code = response.status_code,
                    headers = response.headers
                )

        async with httpx.AsyncClient() as client:
            forwarded = await client.request(
                method=request.method,
                url=url,
                params=request.query_params,
                headers=request.headers,
                content=await request.body()
            )

        if request.method == "GET":
            ttl = 3600
            directives = parse_cache_control_directives(forwarded.headers.get("cache-control") or "")
            max_age = check_directive("max-age", directives)
            if max_age:
                ttl = int(max_age)
            if not check_directive("no-cache", directives) and not check_directive("no-store", directives):
                add_to_cache(cache, url, request.query_params, request.headers, forwarded, forwarded.headers, ttl)

        print("returned from forwarded response")
        return Response(
            content = forwarded.content,
            status_code = forwarded.status_code,
            headers = forwarded.headers,
        )

    return app

if __name__ == "__main__":
    args = parse_args()
    app = create_app(args.origin, args.port)

    uvicorn.run(app, host="0.0.0.0", port=args.port)
