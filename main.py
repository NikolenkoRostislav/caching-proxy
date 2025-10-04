import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from utils import get_from_cache, add_to_cache, parse_args

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
            response = await get_from_cache(cache, url, request)
            if response:
                print("returned from cache")
                return Response(
                    content = response.content,
                    status_code = response.status_code,
                    headers = response.headers
                )

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=url,
                params=request.query_params,
                headers=request.headers,
                content=await request.body()
            )

        if request.method == "GET":
            add_to_cache(cache, url, request, response)

        print("returned from forwarded response")
        return Response(
            content = response.content,
            status_code = response.status_code,
            headers = response.headers,
        )

    return app

if __name__ == "__main__":
    args = parse_args()
    app = create_app(args.origin, args.port)

    uvicorn.run(app, host="0.0.0.0", port=args.port)
