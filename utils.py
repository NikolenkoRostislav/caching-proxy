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
    parser.add_argument(
        "--clear", "-c",
        type=str,
        help="Clear stale/all cache"
    )

    return parser.parse_args()

