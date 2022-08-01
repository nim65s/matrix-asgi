from .server import AsgiMatrixServer


def main():
    """Start everything."""
    AsgiMatrixServer().run()


if __name__ == "__main__":
    main()
