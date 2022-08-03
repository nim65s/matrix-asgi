#!/usr/bin/env python
"""Entry point to start an instrumentalized app for coverage and run tests."""

import argparse
import logging
from os import environ
from subprocess import Popen, run
from time import time

import httpx
import yaml
from synapse._scripts.register_new_matrix_user import request_registration

MATRIX_URL, MATRIX_ID, MATRIX_PW = (
    environ[v] for v in ["MATRIX_URL", "MATRIX_ID", "MATRIX_PW"]
)
FULL_ID = f'@{MATRIX_ID}:{MATRIX_URL.split("/")[2]}'
LOGGER = logging.getLogger("matrix-asgi.tests.start")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "-v", "--verbose", action="count", default=0, help="increment verbosity level"
)


def wait_available(url: str, key: str, timeout: int = 10) -> bool:
    """Wait until a service answer correctly or timeout."""

    def check_json(url: str, key: str) -> bool:
        """Ensure a service is started.

        At a given url answers with valid json including a certain key.
        """
        try:
            data = httpx.get(url).json()
            return key in data
        except httpx.ConnectError:
            return False

    start = time()
    while True:
        if check_json(url, key):
            return True
        if time() > start + timeout:
            return False


def run_and_test():
    """Launch the bot and its tests."""
    # Start the server, and wait for it
    LOGGER.info("Spawning synapse")
    srv = Popen(
        [
            "python",
            "-m",
            "synapse.app.homeserver",
            "--config-path",
            "/srv/homeserver.yaml",
        ]
    )
    if not wait_available(f"{MATRIX_URL}/_matrix/client/r0/login", "flows"):
        return False

    # Register a user for the bot.
    LOGGER.info("Registering the bot")
    with open("/srv/homeserver.yaml") as f:
        secret = yaml.safe_load(f.read()).get("registration_shared_secret", None)
    request_registration(MATRIX_ID, MATRIX_PW, MATRIX_URL, secret, admin=True)

    # Run the main unittest module
    LOGGER.info("Runnig unittests")
    ret = run(["coverage", "run", "./manage.py", "test"], cwd="tests").returncode == 0

    LOGGER.info("Stopping synapse")
    srv.terminate()

    LOGGER.info("Processing coverage")
    for cmd in ["report", "html", "xml"]:
        run(["coverage", cmd])
    return ret


if __name__ == "__main__":
    args = parser.parse_args()
    log_format = "%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s"
    logging.basicConfig(level=50 - 10 * args.verbose, format=log_format)
    exit(not run_and_test())
