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

## Unit tests

```
docker compose -f test.yml up --exit-code-from tests --force-recreate --build
```
