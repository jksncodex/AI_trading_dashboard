import logging
from pathlib import Path

def setup_logging(log_dir: str = "logs") -> None:
    Path(log_dir).mkdir(exists_ok=True)
    logging.basicConfig(
        filename=f"{log_dir}/app_log",
        level=logging.INFO,
        format="%(asctime)s % (levelname)s %(name)s %(message)s",

    )