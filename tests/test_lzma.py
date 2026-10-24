from pathlib import Path

import pytest

from multicompress.engines.lzma_engine import LZMAEngine


@pytest.mark.parametrize(
    "payload",
    [
        b"python test\n" * 500,
        b"\x00\x01\x02\x03" * 1000,
        b"",
    ],
)
def test_lzma_round_trip(tmp_path, payload):
    source = tmp_path / "sample.bin"
    source.write_bytes(payload)

    engine = LZMAEngine()
    compressed = engine.compress_file(source, format_name="lzma")
    assert compressed.exists()

    restored = engine.decompress_file(compressed)
    assert restored.read_bytes() == payload


def test_lzma_supports_xz_format(tmp_path):
    source = tmp_path / "sample.txt"
    source.write_text("texte très répétitif\n" * 40, encoding="utf-8")

    engine = LZMAEngine()
    compressed = engine.compress_file(source, format_name="xz")
    assert compressed.name.endswith(".xz")

    restored = engine.decompress_file(compressed)
    assert restored.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")


def test_lzma_rejects_invalid_format():
    engine = LZMAEngine()
    with pytest.raises(ValueError):
        engine.compress_file(Path("unused.txt"), format_name="unknown")
