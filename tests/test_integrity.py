from pathlib import Path

from multicompress.engines.bzip2_engine import BZip2Engine
from multicompress.engines.lzma_engine import LZMAEngine


def test_bzip2_rejects_truncated_stream(tmp_path):
    source = tmp_path / "input.bin"
    source.write_bytes(b"abc")
    compressed = BZip2Engine().compress_file(source)
    compressed.write_bytes(compressed.read_bytes()[:-1])
    try:
        BZip2Engine().decompress_file(compressed)
    except Exception:
        return
    raise AssertionError("Expected invalid/truncated BZip2 stream to raise")


def test_lzma_rejects_truncated_stream(tmp_path):
    source = tmp_path / "input.bin"
    source.write_bytes(b"abc")
    compressed = LZMAEngine().compress_file(source, format_name="lzma")
    compressed.write_bytes(compressed.read_bytes()[:-5])
    try:
        LZMAEngine().decompress_file(compressed)
    except Exception:
        return
    raise AssertionError("Expected invalid/truncated LZMA stream to raise")
