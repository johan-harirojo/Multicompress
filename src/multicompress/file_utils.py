from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from .exceptions import FileOperationError, ValidationError


def ensure_parent_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def safe_output_path(source: Path, suffix: str, output: str | Path | None = None) -> Path:
    if output is not None:
        target = Path(output)
    else:
        target = source.with_name(f"{source.name}{suffix}")
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {target}")
    ensure_parent_directory(target)
    return target


def atomic_write_bytes(path: Path, data: bytes) -> Path:
    ensure_parent_directory(path)
    fd, temp_path = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", text=False)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(temp_path, path)
    except Exception as exc:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise FileOperationError(f"Failed to write output file: {path}") from exc
    return path


def safe_delete_file(path: Path) -> None:
    if path.exists():
        path.unlink()


def validate_input_file(path: str | os.PathLike[str]) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Input file does not exist: {candidate}")
    if not candidate.is_file():
        raise ValidationError(f"Input path is not a regular file: {candidate}")
    return candidate


def normalize_archive_output(path: str | os.PathLike[str] | None) -> Path | None:
    if path is None:
        return None
    output = Path(path)
    if output.is_absolute():
        return output
    return (Path.cwd() / output).resolve()


def is_within_directory(directory: Path, target: Path) -> bool:
    directory = directory.resolve()
    target = target.resolve()
    try:
        target.relative_to(directory)
        return True
    except ValueError:
        return False


def secure_extract(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(archive_path.parent):
        for name in dirs + files:
            candidate = Path(root) / name
            if not is_within_directory(destination, candidate):
                raise ValidationError(f"Path traversal attempt detected: {candidate}")

    shutil.unpack_archive(str(archive_path), str(destination))
