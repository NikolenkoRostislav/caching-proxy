import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from utils import parse_args

def create_app(origin: str, port: int):
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def proxy(path: str, request: Request):
        print(origin)
        print(port)
        url = f"{origin}/{path}"
        print(url)
        
        #if request.method == "GET":
            #check if request is cached
                #return cached response

        async with httpx.AsyncClient() as client:
            forwarded = await client.request(
                method=request.method,
                url=url,
                params=request.query_params,
                headers=dict(request.headers),
                content=await request.body()
            )

        #if request.method == "GET":
            #cache request and response

        return Response(
            content = forwarded.content,
            status_code = forwarded.status_code,
            headers = dict(forwarded.headers),
        )

    return app


if __name__ == "__main__":
    args = parse_args()
    app = create_app(args.origin, args.port)

    uvicorn.run(app, host="0.0.0.0", port=args.port)
