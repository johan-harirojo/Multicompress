from pathlib import Path

import pytest

from multicompress.engines.bzip2_engine import BZip2Engine


def test_output_exists_without_force_raises(tmp_path):
    source = tmp_path / "sample.txt"
    source.write_text("hello", encoding="utf-8")
    dest = tmp_path / "sample.txt.bz2"
    dest.write_bytes(b"already")

    with pytest.raises(FileExistsError):
        BZip2Engine().compress_file(source, destination=dest)
