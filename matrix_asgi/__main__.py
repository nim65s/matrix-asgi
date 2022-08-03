"""Starting point for the application.

Can be launched from both `python -m matrix_asgi` and `matrix-asgi`.
"""
from .server import AsgiMatrixServer


def main():
    """Start everything."""
    AsgiMatrixServer().run()


if __name__ == "__main__":
    main()
