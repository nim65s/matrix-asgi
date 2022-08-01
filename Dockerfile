FROM python:3.10

WORKDIR /matrix-asgi

ADD . .

RUN --mount=type=cache,sharing=locked,target=/root/.cache python -m pip install .

ENTRYPOINT ["matrix-asgi"]

WORKDIR /app
