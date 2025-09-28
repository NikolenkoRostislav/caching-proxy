import argparse
import asyncio

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

async def main():
    args = parse_args()
    port = args.port
    origin = args.origin

    print(port)
    print(origin)

if __name__ == "__main__":
    asyncio.run(main())