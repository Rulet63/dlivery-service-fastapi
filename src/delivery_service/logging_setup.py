from __future__ import annotations

import logging
import logging.config
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

DEFAULT_LOG_CONFIG_PATH = "/app/log_config.yaml"


def setup_logging(config_path: str = DEFAULT_LOG_CONFIG_PATH) -> None:
    path = Path(config_path)
    if not path.exists():
        logger.warning("Logging config not found: %s, using default logging", path)
        return

    config = yaml.safe_load(path.read_text())
    if not isinstance(config, dict):
        raise ValueError(f"Invalid logging config format in {path}")

    logging.config.dictConfig(config)
