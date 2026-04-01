import logging
import sys
import os


def setup_logger():
    logger = logging.getLogger("shutdown_app")
    logger.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    # File handler
    if not getattr(sys, "frozen", False):
        log_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app.log"
        )
    else:
        log_path = "app.log"

    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


logger = setup_logger()
