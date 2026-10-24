import bz2
from pathlib import Path

import pytest

from multicompress.engines.bzip2_engine import BZip2Engine
from multicompress.exceptions import DecompressionError


@pytest.mark.parametrize(
    "payload",
    [
        b"hello world\n" * 10,
        b"\x00\x01\x02\x03\x04\x05\x06\x07" * 256,
        b"",
    ],
)
def test_bzip2_round_trip(tmp_path, payload):
    source = tmp_path / "sample.bin"
    source.write_bytes(payload)

    engine = BZip2Engine()
    compressed = engine.compress_file(source)
    assert compressed.exists()

    restored = engine.decompress_file(compressed)
    assert restored.read_bytes() == payload


def test_bzip2_rejects_existing_target(tmp_path):
    source = tmp_path / "input.txt"
    source.write_text("bonjour\n")
    destination = tmp_path / "input.txt.bz2"
    destination.write_text("already there")

    engine = BZip2Engine()
    with pytest.raises(FileExistsError):
        engine.compress_file(source, destination=destination)


def test_bzip2_detects_corrupt_stream(tmp_path):
    corrupted = tmp_path / "corrupt.bz2"
    corrupted.write_bytes(b"this is not a valid bzip2 stream")

    engine = BZip2Engine()
    with pytest.raises(DecompressionError):
        engine.decompress_file(corrupted)

    with pytest.raises(OSError):
        bz2.BZ2File(corrupted, "rb").read()  # sanity check
