"""Configuration and shared constants for the project."""

from pathlib import Path

PROJECT_NAME = "multicompress"
VERSION = "0.1.0"
DEFAULT_BZIP2_LEVEL = 9
DEFAULT_LZMA_PRESET = 6
SUPPORTED_LZMA_FORMATS = {"lzma", "xz", "lzma2"}
SAFE_EXTRACTION_ROOT = Path(".")
