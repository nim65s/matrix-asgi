# Matrix ASGI

[![Tests](https://github.com/nim65s/matrix-asgi/actions/workflows/test.yml/badge.svg)](https://github.com/nim65s/matrix-asgi/actions/workflows/test.yml)
[![Lints](https://github.com/nim65s/matrix-asgi/actions/workflows/lint.yml/badge.svg)](https://github.com/nim65s/matrix-asgi/actions/workflows/lint.yml)
[![Release](https://github.com/nim65s/matrix-asgi/actions/workflows/release.yml/badge.svg)](https://pypi.org/project/matrix-asgi)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/nim65s/matrix-asgi/main.svg)](https://results.pre-commit.ci/latest/github/nim65s/matrix-asgi/main)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/nim65s/matrix-asgi/branch/main/graph/badge.svg?token=75XO2X5QW0)](https://codecov.io/gh/nim65s/matrix-asgi)
[![Maintainability](https://api.codeclimate.com/v1/badges/a0783da8c0461fe95eaf/maintainability)](https://codeclimate.com/github/nim65s/matrix-asgi/maintainability)
[![PyPI version](https://badge.fury.io/py/matrix-asgi.svg)](https://badge.fury.io/py/matrix-asgi)

with [matrix-nio](https://github.com/poljar/matrix-nio)

## Install

```
python3 -m pip install matrix-asgi
```

## Use it in your app

You can look at the [models.py](https://github.com/nim65s/matrix-asgi/blob/main/tests/django_app/models.py) and
[consumers.py](https://github.com/nim65s/matrix-asgi/blob/main/tests/django_app/consumers.py) files in the test
application for a simple and quick example.

## Start

Create a matrix user for the bot, and launch this server with the following arguments and/or environment variables
(environment variables update defaults, arguments take precedence):

```
matrix-asgi
# OR
python -m matrix_asgi
```

```
usage: matrix-asgi [-h] [-u MATRIX_URL] -i MATRIX_ID -p MATRIX_PW [-v] application

Matrix ASGI Server.

positional arguments:
  application           The ASGI application instance to use as path.to.module:application

options:
  -h, --help            show this help message and exit
  -u MATRIX_URL, --matrix-url MATRIX_URL
                        matrix homeserver url. Default: `https://matrix.org`.
                        Environment variable: `MATRIX_URL`
  -i MATRIX_ID, --matrix-id MATRIX_ID
                        matrix user-id. Required.
                        Environment variable: `MATRIX_ID`
  -p MATRIX_PW, --matrix-pw MATRIX_PW
                        matrix password. Required.
                        Environment variable: `MATRIX_PW`
  -v, --verbose         increment verbosity level
```

## Unit tests

```
docker compose -f test.yml up --exit-code-from tests --force-recreate --build
```

## JSON Specification

ref. [spec.md](https://github.com/nim65s/matrix-asgi/blob/main/spec.md)

## Changes

ref. [CHANGELOG.md](https://github.com/nim65s/matrix-asgi/blob/main/CHANGELOG.md)
