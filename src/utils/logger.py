import logging
from rich.logging import RichHandler


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    return logging.getLogger("cnpj_analyzer")


logger = setup_logger()
