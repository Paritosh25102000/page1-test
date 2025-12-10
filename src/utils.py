"""
Shared utilities for the ETL pipeline.

Provides logging setup, file I/O, and directory management functions.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def setup_logging(log_dir: str, project_name: str = "etl") -> logging.Logger:
    """
    Set up logging with both file and console handlers.

    Args:
        log_dir: Directory to store log files
        project_name: Name for the log file prefix

    Returns:
        Configured logger instance
    """
    ensure_directory(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{project_name}_{timestamp}.log")

    logger = logging.getLogger("etl")
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    logger.handlers = []

    # File handler - detailed logging
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )
    file_handler.setFormatter(file_format)

    # Console handler - info and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized. Log file: {log_file}")

    return logger


def load_json_file(path: str) -> dict | list:
    """
    Load and parse a JSON file.

    Args:
        path: Path to the JSON file

    Returns:
        Parsed JSON content (dict or list)

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(data: Any, path: str, indent: int = 2) -> None:
    """
    Save data to a JSON file.

    Args:
        data: Data to serialize (dict, list, etc.)
        path: Output file path
        indent: Indentation level for pretty printing
    """
    ensure_directory(os.path.dirname(path))

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def ensure_directory(path: str) -> None:
    """
    Create directory if it doesn't exist.

    Args:
        path: Directory path to create
    """
    if path:
        Path(path).mkdir(parents=True, exist_ok=True)


def get_xml_files(directory: str) -> list[str]:
    """
    Get all XML files in a directory.

    Args:
        directory: Directory to search

    Returns:
        List of absolute paths to XML files, sorted alphabetically
    """
    xml_dir = Path(directory)
    if not xml_dir.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    xml_files = sorted(xml_dir.glob("*.xml"))
    return [str(f.absolute()) for f in xml_files]


def get_project_name_from_file(file_path: str) -> str:
    """
    Extract project name from XML file path.

    The filename (without extension) is used as the project name.

    Args:
        file_path: Path to XML file

    Returns:
        Project name derived from filename
    """
    return Path(file_path).stem


def format_number(value: float, decimals: int = 2) -> float:
    """
    Round a number to specified decimal places.

    Args:
        value: Number to round
        decimals: Number of decimal places

    Returns:
        Rounded number
    """
    if value is None:
        return None
    return round(value, decimals)
