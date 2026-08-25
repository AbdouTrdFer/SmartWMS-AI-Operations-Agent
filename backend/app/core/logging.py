import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def safe_tool_log(logger: logging.Logger, tool_name: str) -> None:
    logger.info("read_only_tool_called", extra={"tool_name": tool_name})
