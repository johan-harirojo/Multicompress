import shutil

import pytest

from multicompress.engines.sevenzip_engine import SevenZipEngine


@pytest.mark.skipif(shutil.which("7z") is None, reason="7z not installed")
def test_sevenzip_round_trip(tmp_path):
    source = tmp_path / "folder"
    source.mkdir()
    (source / "a.txt").write_text("hello from 7z\n", encoding="utf-8")
    (source / "nested").mkdir()
    (source / "nested" / "b.bin").write_bytes(b"\x00\x01\x02\x03")

    archive = tmp_path / "archive.7z"
    engine = SevenZipEngine()
    engine.create_archive(source, archive, method="LZMA2")
    assert archive.exists()
    destination = tmp_path / "restored"
    engine.extract_archive(archive, destination)
    assert (destination / "folder" / "a.txt").exists()
    assert (destination / "folder" / "nested" / "b.bin").exists()

    assert engine.test_archive(archive)
