"""Configuration."""
import argparse
import os


def get_parser(doc):
    """Configure the argument parser from environment and command line."""
    parser = argparse.ArgumentParser(description=doc, prog="matrix-asgi")
    parser.add_argument(
        "-u",
        "--matrix-url",
        default=os.environ.get("MATRIX_URL", "https://matrix.org"),
        help="matrix homeserver url. Default: `https://matrix.org`. "
        "Environment variable: `MATRIX_URL`",
    )
    parser.add_argument(
        "-i",
        "--matrix-id",
        help="matrix user-id. Required. Environment variable: `MATRIX_ID`",
        **(
            {"default": os.environ["MATRIX_ID"]}
            if "MATRIX_ID" in os.environ
            else {"required": True}
        ),
    )
    parser.add_argument(
        "-p",
        "--matrix-pw",
        help="matrix password. Required. Environment variable: `MATRIX_PW`",
        **(
            {"default": os.environ["MATRIX_PW"]}
            if "MATRIX_PW" in os.environ
            else {"required": True}
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increment verbosity level",
    )

    parser.add_argument(
        "application",
        help="The ASGI application instance to use as path.to.module:application",
    )
    return parser
