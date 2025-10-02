import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from utils import parse_args, get_from_cache, add_to_cache

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
            cache_control = forwarded.headers.get("cache-control") or ""
            directives = [d.strip() for d in cache_control.split(",")]
            for d in directives:
                if d.startswith("max-age"):
                    ttl = int(d.split("=")[1])
            if not "no-cache" in directives and not "no-store" in directives:
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
