"""Console and rotating file logging, configured only when a pipeline is run."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

log = logging.getLogger("intermodal")


def setup_logger(log_file: str | Path, level: str = "INFO") -> logging.Logger:
    destination = Path(log_file)
    destination.parent.mkdir(parents=True, exist_ok=True)
    log.setLevel(getattr(logging, level.upper()))
    log.propagate = False
    for handler in list(log.handlers):
        handler.close()
        log.removeHandler(handler)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    file_handler = RotatingFileHandler(destination, maxBytes=10_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    log.addHandler(console)
    log.addHandler(file_handler)
    return log
