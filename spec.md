# Matrix ASGI Message Format

Version: 1.0

## Matrix Connection Scope

- `type`: `"matrix"`
- `asgi["version"]`: `"3.0"`
- `asgi["spec_version"]`: `"1.0"`

## Receive - `receive` event

- `type`: `"matrix.receive"`
- `room`: the room display name
- `user`: the user who wrote the message
- `body`: the message

## Send - `send` event

- `type`: `"matrix.send"`
- `room`: the room id to send the message to
- `body`: the message

## Join - `join` event

- `type`: `"matrix.join"`
- `room`: the room id to join
