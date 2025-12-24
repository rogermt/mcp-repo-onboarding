import logging

# Set up NullHandler to avoid "No handler found" warnings
# when the library is used without logging implementation
logging.getLogger(__name__).addHandler(logging.NullHandler())


def configure_logging(level: int = logging.INFO) -> None:
    """Configure basic logging for the CLI/server."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
