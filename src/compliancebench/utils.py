# Python stdlib
from logging import INFO, Formatter, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Project Dependencies


# Project Imports

def get_logger(
        name: str = "compliance_bench.log", log_to_file=False, log_file_path=None, level=INFO
):
    _FMT = "%(asctime)s [%(levelname)s] (%(module)s:%(lineno)d): %(message)s"
    _DATE = "%a, %Y-%m-%d %I:%M:%S %p"
    log = getLogger(name)
    if log.handlers:  # already configured
        return log
    log.setLevel(level)

    fmt = Formatter(_FMT, datefmt=_DATE)
    # console handler
    console = StreamHandler()
    console.setFormatter(fmt)
    log.addHandler(console)

    if log_to_file:
        path = Path(log_file_path or f"{Project.log_dir}/{name}.log")
        path.parent.mkdir(parents=True, exist_ok=True)
        file_h = RotatingFileHandler(path, maxBytes=20_000_000, backupCount=5)
        file_h.setFormatter(fmt)
        log.addHandler(file_h)

    return log
